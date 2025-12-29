from sqlalchemy import Column, BigInteger, String, Integer, Enum, Float, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.sql import func
from BackEnd.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    school_grade = Column(Integer)
    recent_score = Column(Integer)
    level_tier = Column(Enum('high', 'mid', 'low'))
    daily_avail_time = Column(Integer)
    main_device = Column(Enum('mobile', 'tablet', 'pc'))

class UserTendency(Base):
    __tablename__ = "user_tendency"
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    style_pref = Column(Enum('concept', 'problem'))
    difficulty_pref = Column(Enum('challenge', 'stable'))
    session_breath = Column(Enum('short', 'long'))
    feedback_style = Column(Enum('intuitive', 'analytic'))
    persistence = Column(Integer)
    obstacle_factor = Column(String(255))
    study_goal = Column(String(255))

class UserProfileInfo(Base):
    __tablename__ = "user_profile_info"
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    current_level_tier = Column(String(50))
    prime_tendency = Column(String(100))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class LearningPath(Base):
    __tablename__ = "learning_paths"
    class_id = Column(String(20), primary_key=True)
    title = Column(String(255), nullable=False)
    level_band = Column(String(20))
    target_goal = Column(String(100))
    target_tendency = Column(JSON)

class Content(Base):
    __tablename__ = "contents"
    content_id = Column(BigInteger, primary_key=True, autoincrement=True)
    class_id = Column(String(20), ForeignKey("learning_paths.class_id"))
    title = Column(String(255))
    material_type = Column(Enum('lecture', 'example', 'evaluation', 'supplement'))
    content_func = Column(Enum('remedial', 'core'))
    sequence_no = Column(Integer)

class UserPathAssignment(Base):
    __tablename__ = "user_path_assignment"
    assignment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_profile_info.user_id"), nullable=False)
    class_id = Column(String(20), ForeignKey("learning_paths.class_id"), nullable=False)
    progress_rate = Column(Float, default=0.0)
    status = Column(Enum('assigned', 'in_progress', 'completed', 'paused'))
    assigned_at = Column(TIMESTAMP, server_default=func.now())

class UserLearningLog(Base):
    __tablename__ = "user_learning_log"
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_profile_info.user_id"), nullable=False)
    assignment_id = Column(BigInteger, ForeignKey("user_path_assignment.assignment_id"))
    class_id = Column(String(10))
    event_type = Column(Enum('progress', 'level_change', 'other'))
    prev_val = Column(String(255))
    curr_val = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())