import time
import json
import requests
from analyzer import parse_and_classify
from excel_manager import ExcelManager

def run_data_refining(driver):
    """
    [요청하신 성공 방식 적용]
    Requests를 사용하여 pageType='detail'로 데이터를 확실하게 가져옵니다.
    쿠키는 Selenium에서 빌려옵니다.
    """
    # 1. 대상 학교 리스트 로드
    try:
        with open("filtering_list.json", "r", encoding="utf-8") as f:
            target_list = json.load(f)
    except FileNotFoundError:
        print("❌ filtering_list.json 파일이 없습니다.")
        return

    # 2. 주기 번호 로드
    try:
        with open("session.json", "r", encoding="utf-8") as f:
            period = json.load(f).get("current_period", "40")
    except:
        period = "40"

    em = ExcelManager()
    batch_results = []

    print(f"🚀 총 {len(target_list)}개 학교의 데이터 수집을 시작합니다. (모드: detail)")

    # 3. [핵심] Selenium의 최신 쿠키(JSESSIONID 등)를 Requests로 복사
    # (이렇게 하면 사용자님이 매번 쿠키를 복사붙여넣기 안 해도 됩니다)
    session = requests.Session()
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # 4. 헤더 설정 (사용자님이 주신 성공 코드 기반)
    user_agent = driver.execute_script("return navigator.userAgent")
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.schoolsafe24.or.kr',
        'Referer': 'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltList.do',
        'X-Requested-With': 'XMLHttpRequest'
    })

    # 5. 수집 루프
    for i, school_code in enumerate(target_list):
        # [결정적 수정] pageType을 'detail'로 설정!
        payload = {
            'schlCd': school_code,
            'schdlMngSn': period,
            'pageType': 'detail'  # <--- update가 아니라 detail로 변경!
        }

        try:
            response = session.post(
                'https://www.schoolsafe24.or.kr/mngr/sepr/seprRptRsltSchlInfoPop.do',
                data=payload,
                timeout=10 # 타임아웃 10초로 넉넉하게
            )

            if response.status_code == 200:
                # 데이터가 잘 왔는지 확인하기 위해 길이 체크 (너무 짧으면 로그인 풀림/에러)
                if len(response.text) < 500:
                    print(f"⚠️ {school_code}: 데이터가 너무 짧습니다 (내용 확인 필요)")
                    # 필요시 아래 주석 풀고 내용 확인
                    # print(response.text) 
                
                # 분석기로 넘김
                refined_data = parse_and_classify(response.text, school_code)
                batch_results.append(refined_data)
                
                status = refined_data['진단상태']
                icon = "✅" if "정상" in status else "❌" if "미달" in status else "⚠️"
                print(f"[{i+1}/{len(target_list)}] {icon} {refined_data['학교명']} ({status})")
            
            else:
                print(f"❌ {school_code} 서버 에러: {response.status_code}")

        except Exception as e:
            print(f"❌ {school_code} 통신 오류: {e}")
            # [최적화] 오류 발생 시에도 기록을 남겨, 어떤 학교가 실패했는지 엑셀에서 확인 가능하게 함
            # 상태에 '미달'을 포함시켜 다음 필터링 때 재수집 대상으로 자동 선정됨
            batch_results.append({
                "학교코드": school_code,
                "학교명": "접속실패",
                "전화번호": "-",
                "학교급": "-",
                "진단상태": "❌ 미달(오류)", 
                "미달내역": "통신오류/재확인필요",
                "상세근거": str(e)
            })
        
        # 서버 차단 방지를 위한 미세 딜레이
        time.sleep(0.1)
        
        # 중간 저장
        if (i + 1) % 50 == 0:
            em.save_all_at_once(batch_results)
            batch_results = []
            print("💾 중간 저장 완료")

    # 최종 저장
    if batch_results:
        em.save_all_at_once(batch_results)
    else:
        print("⚠️ 저장할 데이터가 없습니다.")