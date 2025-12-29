import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from BackEnd.database import SessionLocal, engine, Base
from BackEnd.models import User, UserTendency, UserProfileInfo, LearningPath, Content, UserPathAssignment, UserLearningLog
from tqdm import tqdm

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def reset_db():
    print("[INFO] DB 초기화 중...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_full_data(n_users):
    db = SessionLocal()
    
    # 등급별 텍스트 풀 정의
    obstacles = {
        'high': ["심화 문제 해결 능력 부족", "고난도 개념 이해 부족", "오답 정리 시간 부족"],
        'mid': ["기초 개념 복습 필요", "학습 집중력 저하", "풀이 과정의 실수", "문제 풀이 양 부족"],
        'low': ["기초 학습 시간 부족", "공부 습관 미형성", "이전 단계 학습 결손", "학습 의욕 저하"]
    }
    goals = {
        'high': ["최상위권 유지", "경시대회 준비", "심화 과정 마스터", "명문대 진학"],
        'mid': ["상위권 진입", "내신 성적 향상", "평균 점수 유지", "취약 과목 보충"],
        'low': ["기초 탈출", "학습 습관 형성", "과락 방지", "현재 과정 수료"]
    }

    try:
        # 1. 마스터 데이터 확정
        lp_ids = [str(i) for i in range(1, 9)]
        for cid in lp_ids:
            band = "high" if int(cid) > 5 else ("mid" if int(cid) > 2 else "low")
            lp = LearningPath(class_id=cid, title=f"정규 코스 LP {cid}", level_band=band,
                              target_goal=f"{band} 레벨 목표 달성", target_tendency={"diff": int(cid)})
            db.merge(lp)
        db.commit()

        for cid in lp_ids:
            for seq in range(1, 4):
                db.add(Content(class_id=cid, title=f"{cid}-{seq}차시 콘텐츠", 
                               material_type=random.choice(['lecture', 'example', 'evaluation', 'supplement']),
                               content_func='core', sequence_no=seq))
        db.commit()

        # 2. 유저 데이터 생성
        print(f"[INFO] {n_users}명 데이터 생성 중...")
        for i in tqdm(range(n_users), desc="Processing", unit="item"):
            score = random.randint(30, 100)
            if score >= 85: tier = 'high'
            elif score >= 60: tier = 'mid'
            else: tier = 'low'
            
            device = random.choice(['mobile', 'tablet', 'pc'])
            user = User(name=f"User_{i+1:04d}", gender=random.choice(['M', 'F']),
                        school_grade=random.randint(1, 3), recent_score=score,
                        level_tier=tier, daily_avail_time=random.choice([60, 120, 180]), main_device=device)
            db.add(user)
            db.commit()

            persistence = random.randint(3, 5) if tier == 'high' else random.randint(1, 5)
            db.add(UserTendency(user_id=user.user_id, style_pref=random.choice(['concept', 'problem']),
                                difficulty_pref='challenge' if tier == 'high' else 'stable',
                                session_breath='long' if device == 'pc' else 'short',
                                feedback_style=random.choice(['intuitive', 'analytic']),
                                persistence=persistence, obstacle_factor=random.choice(obstacles[tier]),
                                study_goal=random.choice(goals[tier])))

            db.add(UserProfileInfo(user_id=user.user_id, current_level_tier=tier,
                                   prime_tendency="완벽주의형" if persistence >= 4 else random.choice(["자기주도형", "강의의존형"])))
            db.commit()

            pools = {'high': ['6','7','8'], 'mid': ['3','4','5'], 'low': ['1','2']}
            for cid in pools[tier]:
                prog = min(1.0, round(random.uniform(0.1 * persistence, 1.0), 2))
                assign = UserPathAssignment(user_id=user.user_id, class_id=cid, progress_rate=prog,
                                            status='completed' if prog > 0.9 else 'in_progress')
                db.add(assign)
                db.flush()
                db.add(UserLearningLog(user_id=user.user_id, assignment_id=assign.assignment_id,
                                       class_id=cid, event_type='progress', prev_val="0.0", curr_val=str(prog)))
            db.commit()
    finally:
        db.close()

def export_dashboard():
    print("[INFO] 대시보드 리포트 생성 중...")
    df = pd.read_sql("SELECT u.*, ut.persistence, upa.progress_rate FROM users u "
                     "JOIN user_tendency ut ON u.user_id = ut.user_id "
                     "JOIN user_path_assignment upa ON u.user_id = upa.user_id", engine)
    
    plt.figure(figsize=(16, 10))
    plt.subplot(2, 2, 1); sns.boxplot(x='level_tier', y='recent_score', data=df, order=['low', 'mid', 'high']); plt.title('Tier별 성적 분포')
    plt.subplot(2, 2, 2); sns.barplot(x='level_tier', y='progress_rate', data=df, order=['low', 'mid', 'high']); plt.title('Tier별 평균 학습 진척도')
    plt.subplot(2, 2, 3); sns.regplot(x='persistence', y='progress_rate', data=df, x_jitter=0.2); plt.title('성실도 vs 진척도 상관성')
    plt.subplot(2, 2, 4); sns.countplot(x='main_device', hue='level_tier', data=df); plt.title('기기별 사용자 티어 분포')
    plt.tight_layout(); plt.savefig('final_report.png')
    print("[SUCCESS] 'final_report.png' 저장 완료.")

def exec():
    reset_db()
    try:
        n = int(input("생성할 유저 수: "))
        seed_full_data(n)
        export_dashboard()
    except Exception as e:
        print(f"[ERROR] 오류: {e}")