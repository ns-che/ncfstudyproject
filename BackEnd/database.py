from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 본인의 실제 정보로 수정 (SSL 관련 이슈 방지를 위해 옵션 추가)
USER = "root"
PASSWORD = "root"
HOST = "localhost"
PORT = "3306"
DB_NAME = "test_db"

DB_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8mb4&ssl_disabled=True"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()