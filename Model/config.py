import os

# 프로젝트의 루트 디렉토리를 정의
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 자주 사용하는 하위 경로들을 미리 정의
DATA_DIR = os.path.join(BASE_DIR, "Data")
PRETRAIN_DIR = os.path.join(BASE_DIR, "Pretrain")