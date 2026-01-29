import re
from bs4 import BeautifulSoup
from config import get_school_config, HTML_SELECTORS, KEYWORDS

def parse_and_classify(html_content, code):
    """
    서식이 같든 다르든, 키워드(생활안전, 교원 등)를 찾아
    정확한 데이터를 뽑아내는 만능 분석기
    """
    if not html_content:
        return _error(code, KEYWORDS['error_messages']['no_data'])

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 로그인 페이지 감지
    login_keywords = KEYWORDS['error_messages']['login_required']
    if all(keyword in soup.text for keyword in login_keywords):
        return _error(code, KEYWORDS['error_messages']['session_expired'])

    try:
        # [1] 기본 정보
        school_name = "이름미상"
        try:
            school_info = HTML_SELECTORS['school_info']
            name_tag = soup.find("th", string=lambda x: x and school_info['name_label'] in x)
            if name_tag: school_name = name_tag.find_next_sibling("td").text.split('(')[0].strip()
        except: pass

        phone = "-"
        try:
            school_info = HTML_SELECTORS['school_info']
            phone_tag = soup.find("th", string=lambda x: x and school_info['phone_label'] in x)
            if phone_tag: phone = phone_tag.find_next_sibling("td").text.strip()
        except: pass

        school_level = "미분류"
        try:
            school_info = HTML_SELECTORS['school_info']
            level_tag = soup.find("th", string=lambda x: x and school_info['level_label'] in x)
            if level_tag: school_level = level_tag.find_next_sibling("td").text.strip()
        except: pass

        # [2] 지능형 테이블 찾기 (순서가 꼬여도 찾을 수 있음)
        table_class = HTML_SELECTORS['table_class']
        all_tables = soup.select(f"table.{table_class}")
        
        student_tbl = None
        staff_tbl = None
        drill_tbl = None
        
        table_keywords = HTML_SELECTORS['table_keywords']

        for tbl in all_tables:
            txt = tbl.text.replace(" ", "")
            # 학생 교육 테이블 식별
            if all(kw in txt for kw in table_keywords['student_education']):
                student_tbl = tbl
            # 교직원 테이블 식별
            elif all(kw in txt for kw in table_keywords['staff']):
                staff_tbl = tbl
            # 재난훈련 테이블 식별
            elif all(kw in txt for kw in table_keywords['drill']):
                drill_tbl = tbl

        # 테이블을 아예 못 찾았다면? -> 페이지 로딩 실패일 확률 높음
        if not student_tbl and not staff_tbl:
             return _error(code, school_name, KEYWORDS['error_messages']['table_load_fail'])

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
        display_map = {
            "_시": KEYWORDS['data_display']['hours_suffix'],
            "_회": KEYWORDS['data_display']['times_suffix']
        }
        
        for d_key, c_key in check_map.items():
            # 데이터가 없으면 0으로 간주, 기준값(cfg)보다 작으면 미달
            if data.get(d_key, 0) < cfg.get(c_key, 0):
                # "생활안전_시" -> "생활안전(시간)" 처럼 표기 변환 (config 기반)
                display_name = d_key
                for old, new in display_map.items():
                    display_name = display_name.replace(old, new)
                reasons.append(display_name)
                is_fail = True

        # 안전교육 총시간 확인
        education_hours_total = sum(
            data.get(k, 0) for k in data.keys() if k.endswith("_시")
        )
        min_education_hours = cfg.get("안전교육_총시간_기준", 51)
        if education_hours_total < min_education_hours:
            reasons.append(f"교육총시간({education_hours_total}{KEYWORDS['data_display']['duration_short']})")
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

        # 상태 아이콘과 텍스트를 config에서 가져옴
        icon_fail = KEYWORDS['status_icons']['fail']
        icon_warn = KEYWORDS['status_icons']['warning']
        icon_ok = KEYWORDS['status_icons']['success']
        text_fail = KEYWORDS['status_text']['fail']
        text_suspect = KEYWORDS['status_text']['suspect']
        text_normal = KEYWORDS['status_text']['normal']
        
        status = f"{icon_fail} {text_fail}" if is_fail else (f"{icon_warn} {text_suspect}" if is_suspect else f"{icon_ok} {text_normal}")

        return {
            "학교코드": code, "학교명": school_name, "전화번호": phone,
            "학교급": school_level, "진단상태": status,
            "미달내역": ", ".join(reasons),
            "상세근거": f"총시간:{education_hours_total}{KEYWORDS['data_display']['duration_short']} / 이수율:{int(staff_rate*100)}% / 훈련:{total_drill}{KEYWORDS['data_display']['count_short']}"
        }

    except Exception as e:
        return _error(code, school_name, f"{KEYWORDS['error_messages']['analysis_error']}: {str(e)[:10]}")

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