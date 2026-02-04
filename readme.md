# 📚 학교 안전교육 검증 시스템

> 학교별 안전교육 이수 현황을 자동으로 수집, 정제, 분석하여 엑셀 보고서를 생성합니다.

학교안전지원시스템(schoolsafe24.or.kr)에서 학교 정보와 안전교육 이수 현황을 자동으로 수집하고,  
기준값과 비교하여 미달 여부를 판정하는 자동화 시스템입니다.

---

## 🎯 주요 기능

✅ **자동 수집** - Selenium 기반 웹 크롤링 (로그인 이후 학교목록 자동 수집)  
✅ **정제 & 분석** - HTML 파싱 후 시간/횟수 기반 검증  
✅ **판정** - 학교급별 기준값 적용  
✅ **엑셀 생성** - 엑셀 자동 출력 (`안전교육_점검결과_{현재 날짜}.xlsx`)  

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
cd schoolsafe_automatic_analysis

# 가상환경 생성 및 활성화
python -m venv <가상환경명>
.\<가상환경명>\Scripts\activate

+보안 오류시
Set-ExecutionPolicy Unrestricted -Scope Process

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행

```bash
# 전체 실행 (1~4단계 자동 순서 실행)
py src/main.py
```

### 3. 결과 확인

```
data/excel/
├── 안전교육_점검결과_20260101.xlsx
├── 안전교육_점검결과_20260102.xlsx
└── ...
```

---

## 📊 출력 예시

엑셀 파일의 구성:

| 학교코드 | 학교명 | 전화번호 | 학교급 | 진단상태 | 미달내역 | 상세근거 |
|---------|--------|---------|--------|---------|---------|---------|
| 12345 | A초등학교 | 02-1234-5678 | 초등학교 | ✅ 정상 | - | 총시간:55시간 / 이수율:85% |
| 12346 | B중학교 | 02-1234-5679 | 중학교 | ❌ 미달 | 생활안전(시간), 이수율 | 총시간:48시간 / 이수율:65% |

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
