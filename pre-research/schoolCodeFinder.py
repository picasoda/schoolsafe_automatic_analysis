import requests
import re

# 1. 설정 (사용하시던 쿠키와 헤더)
cookies = {
    '4-rr': '0f92bbca08eb1931846a28eaa1521d9f',
    'NetFunnel_ID': '',
    'JSESSIONID': '036D7B66C7A823698360EE8D1E26F5B1.tomcat1', 
}

headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.schoolsafe24.or.kr',
    'Referer': 'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltList.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# 2. 요청 데이터 (전체 목록)
data = [
    ('pageIndex', '1'),
    ('perPage', '100'),
    ('schdlMngSn', '40'),
    ('ctpyCd', '46'),
    ('schlGrdCd', 'SCH00004'),
    ('aprvSttsCd', '1'),
    ('schlCd', ''),  # 전체 조회
]

print("--- 서버에 데이터 요청 중 ---")
response = requests.post(
    'https://www.schoolsafe24.or.kr/mngr/sepr/seprPrvncArSchlLvRptRsltAjaxList.do',
    cookies=cookies,
    headers=headers,
    data=data,
)

print(f"응답 상태 코드: {response.status_code}")

if response.status_code == 200:
    # [진단 1] HTML 원본을 파일로 저장 (눈으로 확인하기 위함)
    filename = "debug_result.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"\n✅ 서버 응답 내용을 '{filename}' 파일로 저장했습니다.")
    print("   -> 이 파일을 VS Code나 브라우저로 열어서 'Q10'으로 검색해보세요.")

    # [진단 2] 패턴 매칭 방식을 바꿔서 'Q' + '숫자' 조합을 무조건 찾기
    # 설명: Q로 시작하고 뒤에 숫자가 5개 이상 오는 모든 문자열을 찾음
    raw_codes = re.findall(r'(Q[0-9]{5,})', response.text)
    
    # 중복 제거
    unique_codes = list(set(raw_codes))

    print("\n[진단 결과]")
    if unique_codes:
        print(f"🎉 성공! 학교 코드 패턴을 {len(unique_codes)}개 찾았습니다.")
        print(f"추출된 코드 예시: {unique_codes[:5]}")
        print("-> 이 방식이 통하면 바로 다음 단계로 넘어가면 됩니다.")
    else:
        print("❌ 실패. 'Q'로 시작하는 코드가 전혀 발견되지 않았습니다.")
        print("-> 저장된 html 파일을 열어 로그인이 풀렸는지, 혹은 데이터가 없는지 확인해야 합니다.")
else:
    print("서버 통신 오류")