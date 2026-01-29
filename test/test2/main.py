import sys
import time
from schoolCodeFinder import run_school_crawler
from excel_manager import ExcelManager
from data_refining import run_data_refining

def main():
    print("=========================================")
    print("   학교 안전교육 자동 점검 시스템 시작")
    print("=========================================")

    # 1. 세션 및 학교 코드 수집 (브라우저 객체를 받아옴)
    print("\n[STEP 1] 로그인 및 학교 코드 수집을 시작합니다...")
    driver = None # 변수 초기화
    try:
        # [핵심] 여기서 driver를 리턴받아 main 함수가 꽉 쥐고 있습니다.
        driver = run_school_crawler()
    except Exception as e:
        print(f"❌ 크롤러 실행 중 오류 발생: {e}")
        if driver: driver.quit() # 오류나면 종료
        return

    # 2. 수집 대상 찾기
    print("\n[STEP 2] 수집 대상 학교를 선별합니다...")
    try:
        em = ExcelManager()
        target_list = em.create_full_list()
        
        if not target_list:
            print("✨ 점검할 대상이 없습니다.")
            driver.quit() # 할 일 없으면 종료
            return
            
    except Exception as e:
        print(f"❌ 목록 설정 중 오류 발생: {e}")
        driver.quit()
        return

    # 3. 데이터 정제 및 엑셀 저장
    print("\n[STEP 3] 상세 데이터 수집 및 정밀 진단을 시작합니다...")
    try:
        # [수정된 부분] driver를 괄호 안에 넣어서 전달합니다!
        if driver:
            run_data_refining(driver)
        else:
            print("❌ 브라우저가 연결되지 않아 정제를 수행할 수 없습니다.")
    except Exception as e:
        print(f"❌ 데이터 정제 중 오류 발생: {e}")

    # 4. 모든 작업 완료 후 브라우저 종료
    print("\n=========================================")
    print("   모든 작업이 완료되었습니다. 브라우저를 종료합니다.")
    print("=========================================")
    
    if driver:
        driver.quit() # 이제 안전하게 종료

if __name__ == "__main__":
    main()