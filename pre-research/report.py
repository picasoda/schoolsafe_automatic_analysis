from bs4 import BeautifulSoup
import os

def 학교급별_기준_설정(학교급):
    """
    [설정부] 학교급별 기준값 정의. 
    기본값을 먼저 설정하고 match문을 통해 특정 학교급만 선택적으로 수정합니다.
    """
    # 모든 학교급 공통 기본 기준 (제공해주신 값 반영)
    config = {
        # --- 학생 안전교육 시간 (시간) ---
        "생활안전교육_시간": 10.0,
        "교통안전교육_시간": 10.0,
        "폭력예방 및 신변보호 교육_시간": 10.0,
        "약물 중독 예방_시간": 7.0,
        "사이버 중독 예방_시간": 3.0,
        "재난안전교육_시간": 6.0,
        "직업안전교육_시간": 3.0,
        "응급처치교육_시간": 2.0,
        
        # --- 학생 안전교육 횟수 (횟수) ---
        "생활안전교육_횟수": 10,
        "교통안전교육_횟수": 10,
        "폭력예방 및 신변보호 교육_횟수": 10,
        "약물 및 사이버 중독 예방_횟수": 10, # 팝업 표 내 통합 횟수 칸 [cite: 40]
        "재난안전교육_횟수": 6,
        "직업안전교육_횟수": 0,
        "응급처치교육_횟수": 2,

        # --- 교직원 및 재난훈련 기준 ---
        "이수율_기준": 0.7,      # 전체 이수율 70% 미만 체크용
        "drill_total_min": 2      # 전체 훈련 횟수 2회 미만 체크용
    }

    # [2] 학교급별 선택적 변경 (Override)
    # match되는 학교급이 없으면 위 기본 설정이 그대로 유지됩니다.
    match 학교급:
        case "중학교":
            config.update({
            })
        case "유치원":
            config.update({
            })
        case "특수학교":
            config.update({
            })
        case "초등학교":
            config.update({
            })

    return config

def extract_popup_data(soup):
    """[추출부] HTML에서 필요한 숫자 데이터(시간, 횟수, 인원, 훈련)를 추출합니다."""
    # 팝업 내 모든 테이블 수집 [cite: 8, 23, 44, 62]
    tables = soup.find_all('table', class_='onTable')
    
    # 1. 학생 안전교육 실적 (시간/횟수) 행 추출 [cite: 36, 39]
    # '시간' 텍스트를 포함한 td의 부모(tr)에서 값 추출
    time_row = soup.find('td', string='시간').parent.find_all('td')[1:-1]
    actual_hours = [float(td.get_text(strip=True) or 0) for td in time_row]
    
    # '횟수' 텍스트를 포함한 td의 부모(tr)에서 값 추출
    count_row = soup.find('td', string='횟수').parent.find_all('td')[1:-1] 
    actual_counts = [float(td.get_text(strip=True) or 0) for td in count_row] 
    
    # 2. 교직원 인원 정보 (세 번째 테이블) [cite: 44, 49, 56]
    staff_tds = tables[2].find_all('td')
    staff_stats = {
        "교원": int(staff_tds[0].text or 0),
        "직원": int(staff_tds[3].text or 0),
        "계약직": int(staff_tds[6].text or 0),
        "교육활동참여자": int(staff_tds[9].text or 0),
        # 교원 + 직원 + 계약직 이수자 합계 
        "이수자_합계": sum([int(staff_tds[1].text or 0), int(staff_tds[4].text or 0), int(staff_tds[7].text or 0)])
    }
    
    # 3. 재난훈련 합계 (네 번째 테이블 마지막 칸) [cite: 62, 78]
    drill_total = int(tables[3].find_all('td')[-1].get_text(strip=True) or 0)
    
    return actual_hours, actual_counts, staff_stats, drill_total

def validate_data(school_name, actual_hours, actual_counts, staff_stats, drill_total, conf):
    """[비교부] 추출된 실제 데이터와 기준(conf)을 비교하여 문제 항목을 리스트로 반환합니다."""
    issues = []
    
    # --- 로직 1: 학생 안전교육 시간 및 횟수 체크 ---
    h_labels = ["생활안전교육_시간", "교통안전교육_시간", "폭력예방 및 신변보호 교육_시간", 
                "약물 중독 예방_시간", "사이버 중독 예방_시간", "재난안전교육_시간", 
                "직업안전교육_시간", "응급처치교육_시간"]
    
    for i, label in enumerate(h_labels):
        if i < len(actual_hours) and actual_hours[i] < conf.get(label, 0):
            issues.append(f"학생시간미달: {label} ({actual_hours[i]} < 기준 {conf[label]})")

    c_labels = ["생활안전교육_횟수", "교통안전교육_횟수", "폭력예방 및 신변보호 교육_횟수", 
                "약물 및 사이버 중독 예방_횟수", "재난안전교육_횟수", "직업안전교육_횟수", "응급처치교육_횟수"]
    
    for i, label in enumerate(c_labels):
        if i < len(actual_counts) and actual_counts[i] < conf.get(label, 0):
            issues.append(f"학생횟수미달: {label} ({actual_counts[i]} < 기준 {conf[label]})")

    # --- 로직 2: 교직원 이수율 및 인원 누락 체크 ---
    total_staff = staff_stats["교원"] + staff_stats["직원"] + staff_stats["계약직"]
    if total_staff > 0:
        pass_rate = staff_stats["이수자_합계"] / total_staff
        if pass_rate < conf["이수율_기준"]:
            issues.append(f"교직원 이수율 저조: {round(pass_rate*100, 1)}% (기준 70% 미만)")
    
    for group in ["교원", "직원", "계약직", "교육활동참여자"]:
        if staff_stats[group] == 0:
            issues.append(f"인원 데이터 누락: {group} 항목이 0명입니다.")

    # --- 로직 3: 재난훈련 합계 체크 ---
    if drill_total < conf["drill_total_min"]:
        issues.append(f"재난훈련 부족: 합계 {drill_total}회 (기준 2회 미만)")

    return issues

def analyze_main(html_content):
    """[실행부] 파싱, 추출, 검증 과정을 조합하여 최종 결과를 출력합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 학교명 및 학교급 추출 [cite: 11, 12]
    school_name = soup.find('td', class_='al').get_text(strip=True).split('(')[0]
    grade = soup.find('th', string='학교급').find_next('td').get_text(strip=True)
    
    # 1. 설정 로드 (함수명 일치 확인)
    conf = 학교급별_기준_설정(grade)
    
    # 2. 데이터 추출
    actual_hours, actual_counts, staff_stats, drill_total = extract_popup_data(soup)
    
    # 3. 데이터 검증
    issues = validate_data(school_name, actual_hours, actual_counts, staff_stats, drill_total, conf)
    
    # 4. 결과 출력
    print(f"\n[진단 결과: {school_name}]")
    if not issues:
        print("  ✅ 모든 항목이 정상입니다.")
    else:
        for issue in issues:
            print(f"  ❌ {issue}")

#=====================================================================테스트
def run_test_with_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 정보 추출 [cite: 11, 12]
    학교명 = soup.find('td', class_='al').get_text(strip=True).split('(')[0] 
    학교급 = soup.find('th', string='학교급').find_next('td').get_text(strip=True) 
    
    # 2. 기준값 및 실제 데이터 로드
    conf = 학교급별_기준_설정(학교급)
    actual_hours, actual_counts, staff_stats, drill_total = extract_popup_data(soup)
    
    print(f"\n" + "="*75)
    print(f" [정밀 검증 테스트] {학교명} ({학교급})")
    print("="*75)

    # --- [대조 1: 학생 안전교육 시간] ---
    print(f"\n[1. 학생 안전교육 시간(차시) 대조]")
    print(f"{'항목명':<25} | {'실제값':>6} | {'목표값':>6} | {'상태'}")
    print("-" * 75)
    h_labels = ["생활안전교육_시간", "교통안전교육_시간", "폭력예방 및 신변보호 교육_시간", 
                "약물 중독 예방_시간", "사이버 중독 예방_시간", "재난안전교육_시간", 
                "직업안전교육_시간", "응급처치교육_시간"]
    
    for i, label in enumerate(h_labels):
        val = actual_hours[i]
        target = conf.get(label, 0)
        status = "✅ 정상" if val >= target else "❌ 미달"
        print(f"{label:<22} | {val:>9.1f} | {target:>9.1f} | {status}")

    # --- [대조 2: 학생 안전교육 횟수] ---
    print(f"\n[2. 학생 안전교육 횟수(회) 대조]")
    print(f"{'항목명':<25} | {'실제값':>6} | {'목표값':>6} | {'상태'}")
    print("-" * 75)
    # 팝업정보.txt의 횟수 행 순서와 일치 (약물/사이버 통합 반영) [cite: 32, 40, 41]
    c_labels = ["생활안전교육_횟수", "교통안전교육_횟수", "폭력예방 및 신변보호 교육_횟수", 
                "약물 및 사이버 중독 예방_횟수", "재난안전교육_횟수", "직업안전교육_횟수", "응급처치교육_횟수"]
    
    for i, label in enumerate(c_labels):
        val = actual_counts[i]
        target = conf.get(label, 0)
        status = "✅ 정상" if val >= target else "❌ 미달"
        print(f"{label:<22} | {val:>9.1f} | {target:>9.1f} | {status}")

    # --- [대조 3: 교직원 이수 실적] ---
    total_staff = staff_stats["교원"] + staff_stats["직원"] + staff_stats["계약직"]
    total_pass = staff_stats["이수자_합계"]
    pass_rate = (total_pass / total_staff) if total_staff > 0 else 0
    
    print(f"\n[3. 교직원 이수 실적 대조]")
    print(f"- 전체 이수율: {pass_rate*100:.1f}% (목표: {conf['이수율_기준']*100:.0f}% 이상) -> {'✅' if pass_rate >= conf['이수율_기준'] else '❌'}")
    for group, count in {"교원": staff_stats["교원"], "직원": staff_stats["직원"], 
                       "계약직": staff_stats["계약직"], "활동참여자": staff_stats["교육활동참여자"]}.items():
        print(f"- {group:10}: {count:>3}명 (인원 존재 여부 체크) -> {'✅' if count > 0 else '⚠️ 확인필요'}")

    # --- [대조 4: 재난대비훈련 합계] ---
    target_drill = conf["drill_total_min"]
    print(f"\n[4. 재난대비훈련 합계 대조]")
    print(f"- 훈련 총 횟수: {drill_total}회 (목표: {target_drill}회 이상) -> {'✅' if drill_total >= target_drill else '❌'}")
    print("="*75)

if __name__ == "__main__":
    # 파일 읽기 및 실행 로직 (기존과 동일)
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, "팝업정보.txt")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                test_html = f.read()
            run_test_with_details(test_html)
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="cp949") as f:
                test_html = f.read()
    else:
        print("❌ '팝업정보.txt' 파일이 없습니다.")