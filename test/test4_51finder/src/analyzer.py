import re
from bs4 import BeautifulSoup
from config import get_school_config

def parse_and_classify(html_content, code):
    """
    서식이 같든 다르든, 키워드(생활안전, 교원 등)를 찾아
    정확한 데이터를 뽑아내는 만능 분석기
    """
    if not html_content:
        return _error(code, "❌ 데이터없음")

    soup = BeautifulSoup(html_content, 'html.parser')
    
    if "로그인" in soup.text and "비밀번호" in soup.text:
        return _error(code, "❌ 세션만료")

    try:
        # [1] 기본 정보
        school_name = "이름미상"
        try:
            name_tag = soup.find("th", string=lambda x: x and "학교명" in x)
            if name_tag: school_name = name_tag.find_next_sibling("td").text.split('(')[0].strip()
        except: pass

        phone = "-"
        try:
            phone_tag = soup.find("th", string=lambda x: x and "연락처" in x)
            if phone_tag: phone = phone_tag.find_next_sibling("td").text.strip()
        except: pass

        school_level = "미분류"
        try:
            level_tag = soup.find("th", string=lambda x: x and "학교급" in x)
            if level_tag: school_level = level_tag.find_next_sibling("td").text.strip()
        except: pass

        # [2] 지능형 테이블 찾기 (순서가 꼬여도 찾을 수 있음)
        all_tables = soup.select("table.onTable")
        
        student_tbl = None
        staff_tbl = None
        drill_tbl = None

        for tbl in all_tables:
            txt = tbl.text.replace(" ", "")
            if "생활안전교육" in txt and "교통안전교육" in txt:
                student_tbl = tbl
            elif "교원" in txt and "직원" in txt:
                staff_tbl = tbl
            elif "화재" in txt and "지진" in txt:
                drill_tbl = tbl

        # 테이블을 아예 못 찾았다면? -> 페이지 로딩 실패일 확률 높음
        if not student_tbl and not staff_tbl:
             return _error(code, school_name, "❌ 테이블_로드실패")

        # [3] 데이터 추출
        data = {}
        
        # 학생 안전교육
        if student_tbl:
            tds = student_tbl.find_all("td")
            if len(tds) >= 18:
                data.update({
                    "생활안전_시": _f(tds[1].text), "교통안전_시": _f(tds[2].text),
                    "폭력신변_시": _f(tds[3].text), "약물중독_시": _f(tds[4].text),
                    "사이버중독_시": _f(tds[5].text), "재난안전_시": _f(tds[6].text),
                    "직업안전_시": _f(tds[7].text), "응급처치_시": _f(tds[8].text),
                    "생활안전_회": _f(tds[11].text), "교통안전_회": _f(tds[12].text),
                    "폭력신변_회": _f(tds[13].text), "약물사이버_회": _f(tds[14].text),
                    "재난안전_회": _f(tds[15].text), "직업안전_회": _f(tds[16].text),
                    "응급처치_회": _f(tds[17].text)
                })

        # 교직원 이수율
        staff_rate = 0.0
        missing_staff = []
        if staff_tbl:
            s_tds = staff_tbl.find_all("td")
            if len(s_tds) >= 8:
                t_total = _i(s_tds[0].text) + _i(s_tds[3].text) + _i(s_tds[6].text)
                t_done = _i(s_tds[1].text) + _i(s_tds[4].text) + _i(s_tds[7].text)
                staff_rate = (t_done / t_total) if t_total > 0 else 0.0
                
                if _i(s_tds[0].text) == 0: missing_staff.append("교원")
                if _i(s_tds[3].text) == 0: missing_staff.append("직원")
                if _i(s_tds[6].text) == 0: missing_staff.append("계약직")

        # 재난훈련
        total_drill = 0
        drill_types_cnt = 0
        
        if drill_tbl:
            d_tds = drill_tbl.find_all("td")
            if d_tds:
                total_drill = _clean_num(d_tds[-1].text)
                
                # 마지막 '계' 칸을 제외하고, 숫자가 1 이상인 칸의 개수를 셈
                for td in d_tds[:-1]:
                    if _clean_num(td.text) > 0:
                        drill_types_cnt += 1

        # [4] 판정 로직 수정
        cfg = get_school_config(school_level)
        reasons = []
        is_fail = False 
        is_suspect = False 

        # [필수 수정] 시간뿐만 아니라 '횟수' 항목도 검사하도록 매핑 추가
        check_map = {
            # --- 시간 기준 ---
            "생활안전_시": "생활안전교육_시간",
            "교통안전_시": "교통안전교육_시간",
            "폭력신변_시": "폭력예방 및 신변보호 교육_시간",
            "약물중독_시": "약물 중독 예방_시간",
            "사이버중독_시": "사이버 중독 예방_시간",
            "재난안전_시": "재난안전교육_시간",
            "직업안전_시": "직업안전교육_시간",
            "응급처치_시": "응급처치교육_시간",
            
            # --- 횟수 기준 (여기가 빠져 있었습니다!) ---
            "생활안전_회": "생활안전교육_횟수",
            "교통안전_회": "교통안전교육_횟수",
            "폭력신변_회": "폭력예방 및 신변보호 교육_횟수",
            "약물사이버_회": "약물 및 사이버 중독 예방_횟수", # 통합 횟수
            "재난안전_회": "재난안전교육_횟수",
            "직업안전_회": "직업안전교육_횟수",
            "응급처치_회": "응급처치교육_횟수"
        }

        # 기존 로직 그대로 사용 가능
        for d_key, c_key in check_map.items():
            # 데이터가 없으면 0으로 간주, 기준값(cfg)보다 작으면 미달
            if data.get(d_key, 0) < cfg.get(c_key, 0):
                # "생활안전_시" -> "생활안전(시)" 처럼 표기 변환
                display_name = d_key.replace("_시", "(시간)").replace("_회", "(횟수)")
                reasons.append(display_name)
                is_fail = True

        # 안전교육 총시간 확인
        education_hours_total = sum(
            data.get(k, 0) for k in data.keys() if k.endswith("_시")
        )
        min_education_hours = cfg.get("안전교육_총시간_기준", 51)
        if education_hours_total < min_education_hours:
            reasons.append(f"교육총시간({education_hours_total}시간)")
            is_fail = True

        min_types = cfg.get("재난대비훈련_종류", 2)
        min_total = cfg.get("재난대비훈련_총합", 3)
        
        if drill_types_cnt < min_types or total_drill < min_total:
            reasons.append(f"훈련(종류{drill_types_cnt}/합계{total_drill})")
            is_fail = True

        if staff_rate < cfg.get("이수율_기준", 1.0):
            reasons.append(f"이수율({int(staff_rate*100)}%)")
            is_suspect = True

        if missing_staff:
            reasons.append(f"누락({','.join(missing_staff)})")

        status = "❌ 미달" if is_fail else ("⚠️ 의심" if is_suspect else "✅ 정상")

        return {
            "학교코드": code, "학교명": school_name, "전화번호": phone,
            "학교급": school_level, "진단상태": status,
            "미달내역": ", ".join(reasons),
            "상세근거": f"총시간:{education_hours_total}시간 / 이수율:{int(staff_rate*100)}% / 훈련:{total_drill}회"
        }

    except Exception as e:
        return _error(code, school_name, f"분석오류: {str(e)[:10]}")

def _f(text):
    """ '10.5시간' 같은 문자열에서도 10.5만 추출 """
    if not text: return 0.0
    try:
        # 숫자와 소수점만 남기고 제거
        clean = re.sub(r'[^0-9.]', '', text)
        return float(clean) if clean else 0.0
    except:
        return 0.0

def _i(text):
    """ '5회' 같은 문자열에서도 5만 추출 """
    if not text: return 0
    try:
        clean = re.sub(r'[^0-9]', '', text)
        return int(clean) if clean else 0
    except:
        return 0

def _clean_num(text):
    if not text: return 0
    nums = re.findall(r'\d+', text)
    return int(nums[-1]) if nums else 0

def _error(code, name="-", msg="오류"):
    return {
        "학교코드": code, "학교명": name, "전화번호": "-",
        "학교급": "-", "진단상태": msg, "미달내역": "-", "상세근거": "-"
    }