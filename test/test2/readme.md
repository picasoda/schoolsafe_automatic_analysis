# 폴더 구조
test2/
├── 📄 analyzer.py                 # 데이터 분석
├── 📄 config.py                   # ⭐ 설정 (DEFAULT_CONFIG, get_school_config)
├── 📄 data_refining.py            # JSON 정제
├── 📄 excel_manager.py            # 엑셀 출력
├── 📄 main.py                     # 메인 진입점
├── 📄 readme.md                   # 설명서
├── 📄 schoolCodeFinder.py         # 학교코드 크롤링
├── 📁 __pycache__/                # Python 캐시
├── 📁 excel/                      # 📊 엑셀 출력 폴더
└── 📁 json/
    ├── school_list.json           # 학교 목록 (크롤링 결과)
    └── session.json    

# 데이터 흐름 & 입출력

1️⃣  **schoolCodeFinder.py** (크롤링)
   ├─ INPUT: 웹사이트 (https://www.schoolsafe24.or.kr)
   ├─ PROCESS: Selenium 자동화 + 사용자 로그인
   └─ OUTPUT: json/school_list.json
   
2️⃣  **data_refining.py** (JSON 정제)
   ├─ INPUT: json/school_list.json + 원본 HTML 파일들
   ├─ PROCESS: HTML 파싱 → 텍스트 데이터 추출
   └─ OUTPUT: 정제된 JSON 데이터 (메모리)
   
3️⃣  **config.py** (기준값 제공)
   ├─ DEFAULT_CONFIG: 전체 학교 공통 기준
   ├─ SCHOOL_SPECIFIC_CONFIG: 학교급별(유치원/초/중/고) 기준
   └─ get_school_config(grade_text): 학교급 매칭 함수
   
4️⃣  **analyzer.py** (분석 & 판정)
   ├─ INPUT: 정제 데이터 + config.get_school_config() 기준값
   ├─ PROCESS: 시간/횟수 검증 → 상태 판정
   │           ❌ 미달 (기준 미충족)
   │           ⚠️  의심 (데이터 부족/오류)
   │           ✅ 정상 (기준 충족)
   └─ OUTPUT: 분석 결과 리스트
   
5️⃣  **excel_manager.py** (결과 저장)
   ├─ INPUT: analyzer.py 분석 결과
   ├─ PROCESS: pandas → openpyxl 변환
   └─ OUTPUT: excel/{학교명}_분석결과.xlsx
   
6️⃣  **main.py** (통합 실행)
   └─ 위 1~5를 순차적으로 실행