"""
【역할】 프로젝트 경로 + 기준값 + API/HTML 서식 통합 관리

【외부 의존성】 None (pathlib만 사용)

【섹션 1】 경로 관리 (line 20-50)
  - PROJECT_ROOT: 프로젝트 루트 디렉토리 (line 20)
  - PATHS: 프로젝트 디렉토리/파일 경로 딕셔너리 (line 25-32)
  - init_directories(): 폴더 자동 생성 함수 (line 35-40)
  - 호환성 변수: JSON_PATH, EXCEL_PATH 등 (line 46-50)

【섹션 2】 학교 기준값 관리 (line 52-127)
  - DEFAULT_CONFIG: 학교 공통 기준값 (line 52-60)
  - SCHOOL_SPECIFIC_CONFIG: 학교급별(유치원/초등/중학) 기준값 (line 63-100)
  - get_school_config(): 학교급 텍스트로 설정값 반환 함수 (line 103-127)

【섹션 3】 API/서식 통합 관리 (line 130-207)
  - API_CONFIG: URL, 헤더, 요청 파라미터, Payload 키 (line 140-165)
  - HTML_SELECTORS: 테이블 클래스, 셀렉터, 키워드 (line 168-182)
  - KEYWORDS: 에러 메시지, 표시 텍스트, 상태 아이콘 (line 185-207)

【수정 시 주의】
  - 새로운 폴더 추가 시 PATHS 딕셔너리에만 추가하면 자동 생성
  - 파일명 변경: PATHS에서 수정
  - URL/헤더 변경: API_CONFIG에서 수정
  - HTML 구조 변경: HTML_SELECTORS/KEYWORDS에서 수정
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
    'backup_dir': PROJECT_ROOT / 'data' / 'backup', 
    
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


# ========== 【API 및 서식 통합 관리】 ==========
"""
【역할】 URL, HTTP 헤더, HTML 셀렉터, 키워드 등 서식 관련 요소 중앙 관리

외부에서 아래 상수들을 import하면 된다:
  from config import API_CONFIG, HTML_SELECTORS, KEYWORDS
"""

# ========== 【API 설정 (URL + 헤더)】 ==========
API_CONFIG = {
    "base_url": "https://www.schoolsafe24.or.kr",
    
    "endpoints": {
        "list_page": "/mngr/sepr/seprPrvncArSchlLvRptRsltList.do",
        "detail_data": "/mngr/sepr/seprRptRsltSchlInfoPop.do",
    },
    
    "headers": {
        "Accept": "text/html, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    },
    
    "request_params": {
        "timeout": 10,
        "delay": 0.1,  # 요청 간격 (초)
    },
    
    "payload_keys": {
        "school_code": "schlCd",
        "period": "schdlMngSn",
        "page_type": "pageType",
        "page_type_value": "detail"
    }
}


# ========== 【HTML 셀렉터 및 태그】 ==========
HTML_SELECTORS = {
    "table_class": "onTable",
    
    # 기본 정보 찾기 (th 태그의 text 기반)
    "school_info": {
        "name_label": "학교명",
        "phone_label": "연락처",
        "level_label": "학교급"
    },
    
    # 테이블 식별 키워드
    "table_keywords": {
        "student_education": ["생활안전교육", "교통안전교육"],
        "staff": ["교원", "직원"],
        "drill": ["화재", "지진"]
    }
}


# ========== 【분석 키워드 및 검증 텍스트】 ==========
KEYWORDS = {
    "error_messages": {
        "login_required": ["로그인", "비밀번호"],
        "data_too_short": "데이터가 너무 짧습니다 (로그인 만료 가능성)",
        "table_load_fail": "❌ 테이블_로드실패",
        "no_data": "❌ 데이터없음",
        "session_expired": "❌ 세션만료",
        "communication_error": "❌ 통신 오류",
        "analysis_error": "분석오류"
    },
    
    "data_display": {
        "hours_suffix": "(시간)",
        "times_suffix": "(횟수)",
        "duration_short": "시간",
        "count_short": "회"
    },
    
    "status_icons": {
        "success": "✅",
        "fail": "❌",
        "warning": "⚠️"
    },
    
    "status_text": {
        "normal": "정상",
        "fail": "미달",
        "suspect": "의심"
    }
}
