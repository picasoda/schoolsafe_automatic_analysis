# 학교 안전교육 검증 시스템

학교별 안전교육 이수 현황을 자동으로 수집, 정제, 분석하여 엑셀 보고서로 생성합니다.

## 📁 폴더 구조

```
test3/
├── src/
│   ├── main.py                    # 통합 실행 (순서 제어)
│   ├── config.py                  # 설정값 + 헬퍼 함수
│   ├── schoolCodeFinder.py        # 웹 크롤링
│   ├── data_refining.py           # 데이터 정제
│   └── analyzer.py                # 분석 & 판정
├── excel_manager.py               # 엑셀 출력
├── requirements.txt               # 의존성
├── README.md                      # 이 파일
├── .gitignore
└── 📁 data/
    ├── json/
    │   ├── school_list.json       # 크롤링 결과
    │   └── session.json           # 브라우저 세션
    └── excel/                     # 출력 폴더
```

## 🔄 데이터 흐름 & 입출력

| 순서 | 모듈 | INPUT | PROCESS | OUTPUT |
|------|------|-------|---------|--------|
| 1️⃣  | `schoolCodeFinder.py` | 웹사이트 (Selenium) | 로그인 + 학교 목록 크롤링 | `json/school_list.json` |
| 2️⃣  | `data_refining.py` | HTML 파일들 | HTML 파싱 → 텍스트 추출 | 정제된 JSON 데이터 |
| 3️⃣  | `config.py` | - | 학교급별 기준값 정의 | DEFAULT_CONFIG, SCHOOL_SPECIFIC_CONFIG |
| 4️⃣  | `analyzer.py` | 정제 데이터 + config 기준값 | 시간/횟수 검증 → 상태 판정 | 분석 결과 (❌/⚠️/✅) |
| 5️⃣  | `excel_manager.py` | 분석 결과 | Pandas + openpyxl 변환 | `excel/{학교명}_분석결과.xlsx` |
| 6️⃣  | `main.py` | - | 위 1~5 순차 실행 | 최종 보고서 |

## 📌 파일별 개요

| 파일 | 역할 | 주요 함수 | 의존성 |
|------|------|---------|--------|
| `main.py` | 실행 순서 제어 | `main()` | config + 모든 모듈 |
| `config.py` | 기준값 관리 | `get_school_config()` | - |
| `schoolCodeFinder.py` | 크롤링 | `scrape_schools()` | selenium |
| `data_refining.py` | 정제 | `refine_data()` | config |
| `analyzer.py` | 분석 | `analyze_school()` | config |
| `excel_manager.py` | 출력 | `save_excel()` | - |

**상세 내용은 각 파일 상단의 주석을 참고하세요.**

## 📋 실행 방법

### 필수 설치
```bash
pip install -r requirements.txt
```

### 전체 실행
```bash
python main.py
```

### 개별 모듈 실행
```bash
python schoolCodeFinder.py
python data_refining.py
python analyzer.py
```

## 📝 파일 상단 주석 템플릿

각 파일의 상단(1~15줄)에 이 형식으로 작성하세요:

```python
"""
【역할】 이 파일이 하는 일

【외부 의존성】
  - from [file] import [func]
  - import [library]

【내부 정의】
  - [변수/상수명]: [타입] (line X-Y)
  - [함수명](): [설명] (line X-Y)

【수정 시 주의】
  - [다른 파일]의 참조 업데이트 필요
  - [설정값] 변경 시 [파일]도 수정
"""
```

## ⚠️ 주의사항

- ❗ 첫 실행 시 Selenium 자동화 중 수동 로그인 필요
- 📌 학교급 추가 시 config.py의 기준값 수정 필요
- ⚠️ 엑셀 파일이 이미 있으면 덮어씀
- 🔗 main.py는 순서 제어만, 비즈니스 로직은 각 모듈에