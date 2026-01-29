# [프로젝트명]

[한 문장으로 이 프로젝트의 목적을 설명하세요]

## 📁 폴더 구조 (표준 형식)

```
project_name/
├── src/                           # 소스 코드
│   ├── main.py (or index.js, etc)
│   ├── config.py
│   └── [module].py
├── tests/                         # 테스트 코드
│   └── test_[module].py
├── data/                          # 입력 데이터
│   └── [input_files]
├── output/                        # 출력 결과
│   └── [output_files]
├── docs/                          # 문서/설명서
│   └── [documentation]
├── config/                        # 설정 파일
│   └── settings.json (or .env, etc)
├── README.md                      # 프로젝트 설명
├── .gitignore                     # Git 무시 파일
└── requirements.txt (or package.json, etc)  # 의존성
```

## 🔄 데이터 흐름 & 입출력

| 순서 | 모듈 | INPUT | PROCESS | OUTPUT |
|------|------|-------|---------|--------|
| 1️⃣  | `[module1]` | [입력] | [처리] | [중간결과] |
| 2️⃣  | `[module2]` | [중간결과] | [처리] | [분석결과] |
| 3️⃣  | `[module3]` | [분석결과] | [처리] | [최종결과] |

## 📌 파일별 개요

| 파일 | 역할 | 주요 함수 | 의존성 |
|------|------|---------|--------|
| `main` | 실행 순서 제어 | `main()` | config + 모든 모듈 |
| `config` | 설정값 관리 | `get_[option]()` | - |
| `[module1]` | [역할] | `[func]()` | [의존] |
| `[module2]` | [역할] | `[func]()` | [의존] |
| `[module3]` | [역할] | `[func]()` | [의존] |

**상세 내용은 각 파일 상단의 주석을 참고하세요.**

## 📋 실행 방법

### 필수 설치
```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

### 전체 실행
```bash
# Python
python src/main.py

# Node.js
npm start
```

### 개별 모듈 테스트
```bash
# Python
python src/[module_name].py

# Node.js
npm test
```

## 📝 파일 상단 주석 템플릿

### Python 예시
```python
"""
【역할】 이 파일이 하는 일

【외부 의존성】
  - from [file1] import [func]
  - import [library]

【내부 정의】
  - [변수/상수명]: [타입] (line X-Y)
  - [함수명](): [설명] (line X-Y)

【수정 시 주의】
  - [다른 파일]의 참조 업데이트 필요
  - [설정값] 변경 시 [파일]도 수정
"""
```

### JavaScript 예시
```javascript
/**
 * 【역할】 이 파일이 하는 일
 * 
 * 【외부 의존성】
 *   - import { func } from './file1'
 *   - import library from 'library'
 * 
 * 【내부 정의】
 *   - [변수명]: [타입] (line X-Y)
 *   - [함수명](): [설명] (line X-Y)
 * 
 * 【수정 시 주의】
 *   - [다른 파일]의 참조 업데이트 필요
 */
```

## ⚠️ 주의사항

- ❗ main은 **실행 순서만 제어** (1~10줄)
- 📌 config는 **설정값 + 헬퍼 함수**만 포함
- 🔗 각 모듈은 **의존성을 파일 상단에 명시**
- 📍 모듈 간 순환 참조 금지
