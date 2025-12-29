import scipy.sparse as sp
import numpy as np
from collections import defaultdict
from BackEnd.database import SessionLocal
from BackEnd.models import UserPathAssignment, UserProfileInfo, User
import random

class Dataset(object):
    def __init__(self):
        # DB에서 직접 데이터를 로드합니다.
        self.trainMatrix, self.testRatings = self._load_db_interactions()
        self.traindict = defaultdict(list)
        for u, i in self.trainMatrix.keys():
            self.traindict[u].append(i)
        self.testNegatives = self._generate_db_negatives()
        self.usermeta = self._load_db_usermeta()
        self.num_users, self.num_items = self.trainMatrix.shape

    def _load_db_interactions(self):
        db = SessionLocal()
        # 모든 배정 정보 가져오기
        assignments = db.query(UserPathAssignment).all()
        
        # 유저별 마지막 데이터를 Test로 사용하기 위한 그룹화
        user_data = defaultdict(list)
        max_u, max_i = 0, 0
        for row in assignments:
            u, i = int(row.user_id), int(row.class_id)
            user_data[u].append(i)
            max_u, max_i = max(max_u, u), max(max_i, i)
            
        mat = sp.dok_matrix((max_u + 1, max_i + 1), dtype=np.float32)
        test_ratings = []
        
        for u, items in user_data.items():
            # 마지막 하나는 Test, 나머지는 Train
            test_item = items[-1]
            test_ratings.append([u, test_item])
            for train_item in items[:-1]:
                mat[u, train_item] = 1.0
        
        db.close()
        return mat, test_ratings

    def _generate_db_negatives(self):
        # Test 데이터에 대응하는 99개의 negative 샘플 생성 (추천 시스템 관례)
        negativeList = []
        all_items = set(range(1, 9))
        for u, pos_item in self.testRatings:
            negatives = list(all_items - {pos_item}- set(self.traindict[u]))
            negativeList.append(random.sample(negatives, min(len(negatives), 4)))
        return negativeList

    def _load_db_usermeta(self):
        db = SessionLocal()
        metadict = {}
        profiles = db.query(UserProfileInfo).all()
        for p in profiles:
            # {user_id: [tier, [assigned_list]]}
            metadict[p.user_id] = [p.current_level_tier, []] 
        db.close()
        return metadict