import pandas as pd
import os
import json
from datetime import datetime
import config

class ExcelManager:
    def __init__(self):
        # 1. 관리할 폴더명 정의
        self.excel_dir = config.EXCEL_PATH
        self.json_dir = config.JSON_PATH

        # 2. 폴더가 없으면 자동으로 생성
        os.makedirs(self.excel_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)

        # 3. 엑셀 파일 경로 설정 (excel 폴더 안에 저장)
        today_str = datetime.now().strftime("%Y%m%d")
        self.file_name = os.path.join(self.excel_dir, f"안전교육_점검결과_{today_str}.xlsx")
        
        # 컬럼 정의 ('점검일시' 제외)
        self.columns = ["학교코드", "학교명", "전화번호", "학교급", "진단상태", "미달내역", "상세근거"]

    def create_full_list(self, json_filename=config.SCHOOL_LIST_FILE): # [변경] 기본값 교체
        """
        json 폴더 안에 있는 학교 리스트를 읽어서 반환만 합니다.
        (별도의 파일 저장은 하지 않습니다)
        """
        # json 폴더 경로와 파일명 결합
        full_path = os.path.join(self.json_dir, json_filename)

        # 파일이 실제로 있는지 확인
        if not os.path.exists(full_path):
            print(f"❌ 오류: '{full_path}' 파일을 찾을 수 없습니다.")
            print(f"👉 '{json_filename}' 파일을 '{self.json_dir}' 폴더 안으로 옮겨주세요!")
            return []

        with open(full_path, "r", encoding="utf-8") as f:
            full_list = json.load(f)

        # [수정] 파일 저장 로직 제거 -> 바로 리스트 반환
        print(f"📊 [전체 모드] 총 {len(full_list)}개 학교 데이터를 로드했습니다.")
        
        return full_list

    def save_all_at_once(self, refined_results):
        """
        메모리에 저장된 데이터를 엑셀 폴더 내의 파일에 저장합니다.
        """
        if not refined_results:
            print("⚠️ 저장할 데이터가 없습니다.")
            return

        # 파일이 있으면 읽고, 없으면 새로 생성
        if os.path.exists(self.file_name):
            try:
                df_existing = pd.read_excel(self.file_name, dtype={"학교코드": str})
            except Exception:
                df_existing = pd.DataFrame(columns=self.columns)
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        df_new = pd.DataFrame(refined_results)

        # 데이터 통합 (중복된 학교코드는 최신 정보로 덮어쓰기)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["학교코드"], keep="last")

        try:
            # 정의된 컬럼 순서대로 정렬하여 저장
            df_combined = df_combined[self.columns]
            df_combined.to_excel(self.file_name, index=False)
            print(f"✅ 엑셀 저장 완료: {self.file_name} (총 {len(df_combined)}건)")
        except PermissionError:
            print(f"❌ 저장 실패: {self.file_name} 파일이 열려 있습니다. 닫고 다시 실행하세요.")
        except Exception as e:
            print(f"❌ 저장 중 오류 발생: {e}")

# 테스트 실행부
if __name__ == "__main__":
    em = ExcelManager()
    em.create_full_list()