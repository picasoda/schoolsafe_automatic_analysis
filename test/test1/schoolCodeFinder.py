import json
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 

def run_school_crawler():
    # 1. 환경 설정 및 로그인
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # 필요시 주석 해제
    driver = webdriver.Chrome(options=chrome_options)

    print("--- 브라우저를 실행합니다. 로그인을 완료해주세요 ---")
    driver.get("https://www.schoolsafe24.or.kr/mngr/main/login.do")

    input("로그인을 완료하고 학교 목록 페이지로 이동한 후 Enter를 누르세요...")

    # 2. [자동화] 주기 번호(schdlMngSn) 추출
    try:
        period_element = driver.find_element(By.CLASS_NAME, "chkBox")
        current_period = period_element.get_attribute("data-schdlMngSn")
        print(f"🔎 현재 주기 번호(schdlMngSn) 자동 감지: {current_period}")
    except Exception as e:
        current_period = "40" 
        print(f"⚠️ 주기 번호 추출 실패, 기본값({current_period})을 사용합니다.")

    # 3. [핵심] NetFunnel 등 보안 쿠키를 포함한 전체 세션 복제
    selenium_cookies = driver.get_cookies()
    user_agent = driver.execute_script("return navigator.userAgent")

    session_cookies = {ck['name']: ck['value'] for ck in selenium_cookies}
    
    # request.txt 기반의 '진짜' 헤더 (User-Agent, Referer 필수)
    session_headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.schoolsafe24.or.kr',
        'Referer': 'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltList.do'
    }

    # 세션 정보 저장
    session_bundle = {
        "cookies": session_cookies,
        "headers": session_headers,
        "current_period": current_period
    }

    with open("session.json", "w", encoding="utf-8") as f:
        json.dump(session_bundle, f, ensure_ascii=False, indent=4)
    print("✅ 세션 정보(session.json) 저장 완료")

    # 4. 학교 코드 명단 수집 (request.txt 반영)
    payload = {
        'menuSn': '',
        'upperMenuSn': '',
        'pageIndex': '1',
        'listType': '',
        'schdlMngSn': current_period, # 자동감지된 번호 사용
        'ctpyCd': '46',     # 전라남도 코드
        'eduofCd': '',
        'schlGrdCd': '',
        'schlOperSttsCd': '',
        'schlNm': '',
        'aprvSttsCd': '1', # 제출 한정
        'perPage': '1400'   # 한 번에 긁어오기 위한 시도 (서버가 무시하면 loop 필요할 수도 있음)
    }

    print("📡 학교 목록 서버 요청 중...")
    response = requests.post(
        'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltAjaxList.do',
        cookies=session_cookies,
        headers=session_headers,
        data=payload
    )

    if response.status_code == 200:
        # 학교목록.txt 분석 로직
        # 1차 시도: 체크박스 데이터 속성으로 추출 (가장 정확)
        unique_codes = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            chk_boxes = soup.find_all('input', class_='chkBox')
            for chk in chk_boxes:
                code = chk.get('data-schlCd') 
                if code and code not in unique_codes:
                    unique_codes.append(code)
        except:
            pass
            
        # 2차 시도: 정규식으로 비상 추출 (javascript:goDetail 부분)
        if not unique_codes:
            unique_codes = list(set(re.findall(r'goDetail\("([A-Z][0-9]+)"', response.text)))

        # 결과 저장
        if unique_codes:
            with open("school_list.json", "w", encoding="utf-8") as f:
                json.dump(unique_codes, f, ensure_ascii=False, indent=4)
            print(f"🎉 성공! {len(unique_codes)}개의 학교 코드를 확보했습니다.")
        else:
            print("⚠️ 학교 코드를 찾지 못했습니다. (응답 내용 확인 필요)")
            # 디버깅을 위해 응답 일부 출력
            print(response.text[:500])
            
    else:
        print(f"❌ 요청 실패: {response.status_code}")

    return driver

if __name__ == "__main__":
    run_school_crawler()