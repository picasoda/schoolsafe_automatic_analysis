import requests

cookies = {
    '4-rr': '0f92bbca08eb1931846a28eaa1521d9f',
    'NetFunnel_ID': '',
    'JSESSIONID': '036D7B66C7A823698360EE8D1E26F5B1.tomcat1',
}

headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ko-KR;q=0.7,zh-CN;q=0.6,zh;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'DNT': '1',
    'Origin': 'https://www.schoolsafe24.or.kr',
    'Referer': 'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltList.do',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': '4-rr=0f92bbca08eb1931846a28eaa1521d9f; NetFunnel_ID=; JSESSIONID=966362504240A1ADA48EB90947160BC1.tomcat1',
}

data = {
    'schlCd': 'Q100000165',
    'schdlMngSn': '40',
    'pageType': 'detail',
}

response = requests.post(
    'https://www.schoolsafe24.or.kr/mngr/sepr/seprRptRsltSchlInfoPop.do',
    cookies=cookies,
    headers=headers,
    data=data,
)

print(f"상태 코드: {response.status_code}")

# 2. 결과 내용 출력
if response.status_code == 200:
    # 한글 깨짐 방지 (필요 시)
    response.encoding = 'utf-8' 
    
    print("\n[ 데이터 수신 성공! 내용 확인 ]")
    print("-" * 50)
    print(response.text) # 여기에 HTML 코드가 좌르륵 나오면 성공입니다!
    print("-" * 50)
else:
    print("요청 실패.. 쿠키(JSESSIONID)가 만료되었는지 확인해주세요.")