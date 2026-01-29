"""
【역할】 프로젝트 경로 + 기준값 관리

【외부 의존성】 None

【내부 정의】
  - PATHS: 프로젝트 디렉토리/파일 경로 (line 18-29)
  - init_directories(): 폴더 자동 생성 (line 31-35)
  - DEFAULT_CONFIG: 학교 공통 기준값 (line 38-60)
  - SCHOOL_SPECIFIC_CONFIG: 학교급별 기준값 (line 62-100)
  - get_school_config(): 학교급 기준값 반환 함수 (line 103-117)

【수정 시 주의】
  - 새로운 폴더 추가 시 PATHS 딕셔너리에만 추가하면 자동 생성됨
  - 파일명 변경 필요 시 PATHS에서 수정
"""

from pathlib import Path

# ========== 【프로젝트 루트】 ==========
PROJECT_ROOT = Path(__file__).parent.parent


# ========== 【경로 관리 (쉽게 확장 가능)】 ==========
PATHS = {
    # 디렉토리
    'data_dir': PROJECT_ROOT / 'data',
    'json_dir': PROJECT_ROOT / 'data' / 'json',
    'excel_dir': PROJECT_ROOT / 'data' / 'excel',
    'backup_dir': PROJECT_ROOT / 'data' / 'backup',  # 추가 가능
    
    # 파일
    'school_list_json': PROJECT_ROOT / 'data' / 'json' / 'school_list.json',
    'session_json': PROJECT_ROOT / 'data' / 'json' / 'session.json',
}


# ========== 【폴더 자동 생성】 ==========
def init_directories():
    """필요한 디렉토리 자동 생성"""
    for key, path in PATHS.items():
        if 'dir' in key:  # 'dir'이 들어간 것들만 (파일은 제외)
            path.mkdir(parents=True, exist_ok=True)


# 프로젝트 시작 시 폴더 생성
init_directories()


# ========== 【호환성: 기존 코드 지원】 ==========
JSON_PATH = PATHS['json_dir']
EXCEL_PATH = PATHS['excel_dir']
TARGET_FILE_PATH = PATHS['school_list_json']
SESSION_FILE_PATH = PATHS['session_json']
SCHOOL_LIST_FILE = "school_list.json"


# ========== 【학교급별 기준값】 ==========
DEFAULT_CONFIG = {
    # --- 학생 안전교육 시간 (시간) ---
    "생활안전교육_시간": 10.0,
    "교통안전교육_시간": 10.0,
    "폭력예방 및 신변보호 교육_시간": 10.0,
    "약물 중독 예방_시간": 7.0,
    "사이버 중독 예방_시간": 3.0,
    "재난안전교육_시간": 6.0,
    "직업안전교육_시간": 3.0,
    "응급처치교육_시간": 2.0,
        
    # --- 학생 안전교육 횟수 (횟수) ---
    "생활안전교육_횟수": 2,
    "교통안전교육_횟수": 3,
    "폭력예방 및 신변보호 교육_횟수": 2,
    "약물 및 사이버 중독 예방_횟수": 2,
    "재난안전교육_횟수": 2,
    "직업안전교육_횟수": 1,
    "응급처치교육_횟수": 1,

    # --- 교직원 및 재난훈련 기준 ---
    "이수율_기준": 0.7,
    "재난대비훈련_총합": 3,
    "재난대비훈련_종류": 2
}


SCHOOL_SPECIFIC_CONFIG = {
    "유치원": {
        "생활안전교육_시간": 13.0,
        "교통안전교육_시간": 10.0,
        "폭력예방 및 신변보호 교육_시간": 8.0,
        "약물 중독 예방_시간": 5.0,
        "사이버 중독 예방_시간": 5.0,
        "재난안전교육_시간": 6.0,
        "직업안전교육_시간": 2.0,
        "응급처치교육_시간": 2.0
    },
    "초등학교": {
        "생활안전교육_시간": 12.0,
        "교통안전교육_시간": 11.0,
        "폭력예방 및 신변보호 교육_시간": 8.0,
        "약물 중독 예방_시간": 5.0,
        "사이버 중독 예방_시간": 5.0,
        "재난안전교육_시간": 6.0,
        "직업안전교육_시간": 2.0,
        "응급처치교육_시간": 2.0
    },
    "중학교": {
        "생활안전교육_시간": 10.0,
        "교통안전교육_시간": 10.0,
        "폭력예방 및 신변보호 교육_시간": 10.0,
        "약물 중독 예방_시간": 6.0,
        "사이버 중독 예방_시간": 4.0,
        "재난안전교육_시간": 6.0,
        "직업안전교육_시간": 3.0,
        "응급처치교육_시간": 2.0
    }
}


def get_school_config(grade_text: str) -> dict:
    """
    학교급 텍스트를 분석하여 적합한 config 딕셔너리를 반환합니다.
    
    Args:
        grade_text: 학교급 텍스트 (예: "초등학교", "중학교")
    
    Returns:
        dict: 해당 학교급의 기준값
    """
    # 기본값 복사
    selected_config = DEFAULT_CONFIG.copy()
    
    # 학교급 매칭 (문자열 포함 여부로 유연하게 판단)
    for grade_key, override_values in SCHOOL_SPECIFIC_CONFIG.items():
        if grade_key in grade_text:
            selected_config.update(override_values)
            break
            
    return selected_config
