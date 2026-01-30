# 📚 학교 안전교육 검증 시스템

> 학교별 안전교육 이수 현황을 자동으로 수집, 정제, 분석하여 엑셀 보고서를 생성합니다.

학교안전지원시스템(schoolsafe24.or.kr)에서 학교 정보와 안전교육 이수 현황을 자동으로 수집하고,  
기준값과 비교하여 미달 여부를 판정하는 완전 자동화 시스템입니다.

---

## 🎯 주요 기능

✅ **자동 수집** - Selenium 기반 웹 크롤링 (로그인 + 학교목록 수집)  
✅ **정제 & 분석** - HTML 파싱 후 시간/횟수 기반 검증  
✅ **지능형 판정** - 학교급별 기준값 적용  
✅ **보고서 생성** - 엑셀 자동 출력 (`안전교육_점검결과_{현재 날짜}.xlsx`)  

---

## 📁 프로젝트 구조

```
prod/
├── src/                          # 소스코드 폴더
│   ├── main.py                   # 통합 실행 (순서 제어)
│   ├── config.py                 # 설정값 + 기준값 관리
│   ├── schoolCodeFinder.py       # 웹 크롤링 (Selenium)
│   ├── data_refining.py          # HTML 파싱 & 데이터 정제
│   ├── analyzer.py               # 데이터 분석 & 판정
│   └── excel_manager.py          # 엑셀 출력
│
├── data/                         # 데이터 폴더 (자동 생성)
│   ├── json/
│   │   ├── school_list.json      # 크롤링 결과 학교 목록
│   │   └── session.json          # 브라우저 세션 정보
│   ├── excel/                    # 분석 결과 엑셀 파일
│   └── backup/                   # 이전 결과 백업
│
├── requirements.txt              # 의존성
└── README.md                     # 이 파일
```

### 각 단계별 설명

| 단계 | 파일 | 역할 | 입력 | 출력 |
|------|------|------|------|------|
| **1** | `schoolCodeFinder.py` | 학교 목록 수집 | 웹사이트 로그인 | `school_list.json` |
| **2** | `data_refining.py` | HTML 파싱 & 정제 | 학교별 HTML 응답 | 정제된 팝업 데이터 |
| **3** | `analyzer.py` | 기준값 비교 & 판정 | 정제 데이터 + config | ✅/⚠️/❌ 결과 |
| **4** | `excel_manager.py` | 엑셀 생성 | 분석 결과 | `.xlsx` 파일 |
| **제어** | `main.py` | 1~4 순차 실행 | - | 최종 보고서 |

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/picasoda/schoolsafe_automatic_analysis.git
cd school-safety-automation

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행

```bash
# 전체 실행 (1~4단계 자동 순서 실행)
python src/main.py
```

### 3. 결과 확인

```
data/excel/
├── 안전교육_점검결과_20260101.xlsx
├── 안전교육_점검결과_20260102.xlsx
└── ...
```

---

## ⚙️ 설정 (config.py)

모든 설정값은 `src/config.py`에서 통합 관리됩니다.

### 기본 기준값 (DEFAULT_CONFIG)

```python
"생활안전교육_시간": 10.0,      # 최소 10시간
"교통안전교육_시간": 10.0,
"이수율_기준": 0.7,             # 교직원 70% 이상
"재난대비훈련_종류": 2,          # 최소 2가지
"재난대비훈련_총합": 3           # 최소 3회
```

### 학교급별 기준값 (SCHOOL_SPECIFIC_CONFIG)

```python
"유치원": { "생활안전교육_시간": 13.0, ... }
"초등학교": { "생활안전교육_시간": 12.0, ... }
"중학교": { "생활안전교육_시간": 10.0, ... }
```

### API/HTML 서식 (API_CONFIG, HTML_SELECTORS)

```python
API_CONFIG['base_url']          # 웹사이트 주소
API_CONFIG['endpoints']         # API 엔드포인트
HTML_SELECTORS['table_class']   # HTML 테이블 셀렉터
KEYWORDS['status_icons']        # 상태 아이콘 (✅/❌/⚠️)
```

> 💡 **팁**: 웹사이트 구조가 변경되면 `config.py`의 셀렉터/키워드만 수정하면 됩니다.

---

## 📊 출력 예시

엑셀 파일의 구성:

| 학교코드 | 학교명 | 전화번호 | 학교급 | 진단상태 | 미달내역 | 상세근거 |
|---------|--------|---------|--------|---------|---------|---------|
| 12345 | A초등학교 | 02-1234-5678 | 초등학교 | ✅ 정상 | - | 총시간:55시간 / 이수율:85% |
| 12346 | B중학교 | 02-1234-5679 | 중학교 | ❌ 미달 | 생활안전(시간), 이수율 | 총시간:48시간 / 이수율:65% |

---

## 📝 주요 함수

### config.py
- `get_school_config(grade_text)` - 학교급 기준값 반환

### schoolCodeFinder.py  
- `scrape_schools(driver)` - 학교 목록 크롤링 & JSON 저장

### data_refining.py
- `run_data_refining(driver)` - HTML → 정제 데이터

### analyzer.py
- `parse_and_classify(html_content, code)` - 분석 & 판정

### excel_manager.py
- `save_all_at_once(results)` - 엑셀 파일 생성

### main.py
- `main()` - 1~4단계 순차 실행

---

## ⚠️ 주의사항

### 필수 사항
- ❗ **첫 실행 시**: Selenium 자동화 도중 수동 로그인 필요  
  (진행 상황을 보며 기다리면 자동으로 계속됩니다)

- 🔐 **로그인 정보**: 본인의 학교안전지원시스템 계정 필요

### 설정 수정
- 📌 **새로운 학교급 추가**: `config.py`의 `SCHOOL_SPECIFIC_CONFIG`에 추가
- 🔗 **웹사이트 구조 변경**: `config.py`의 `HTML_SELECTORS` 업데이트
- 📊 **기준값 변경**: `config.py`의 `DEFAULT_CONFIG` 수정

---
