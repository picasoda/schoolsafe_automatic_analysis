# 파일 작성,작동 순서
1. shcoolCodeFinder.py -> school_list.json, session.json
2. excel_manager.py <- school_list.json
-> filtering_list.json
3. cofig.py
4. analyzer.py <- config.py
5. data_refining.py <- analyer.py, filtering_list.json, session.json
6. excel_manager.py <- data_refining.py

# 파일별 주요 로직
1. config.py: 학교급별(초/중/고 등) 안전교육 이수 시간 및 횟수 등 여러 기준치를 정의합니다. 

2. schoolCodeFinder.py: selenium을 통해 실시간으로 세션을 가져옴

3. data_refining.py: 수집된 원본 HTML 파일들을 읽어 분석 가능한 텍스트 데이터로 1차 정제합니다.

4. analyzer.py: html파일을 정제하고 config.py의 기준과 비교하여 ❌ 미달, ⚠️ 의심, ✅ 정상 상태를 판정합니다.

5. excel_manager.py: 최종 분석 결과 리스트를 엑셀 파일로 변환하여 저장합니다.

6. main.py: 이 파일을 실행하면 모든 모듈이 통합되어 작동합니다.