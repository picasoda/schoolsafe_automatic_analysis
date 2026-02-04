import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# config 임포트
sys.path.insert(0, str(Path(__file__).parent / 'src'))
import config


class ExcelManager:
    def __init__(self):
        # PATHS에서 바로 가져오기 (간단!)
        self.excel_dir = config.PATHS['excel_dir']
        self.json_dir = config.PATHS['json_dir']
        
        # 파일명 (고정)
        today_str = datetime.now().strftime("%Y%m%d")
        self.file_name = self.excel_dir / f"안전교육_점검결과_{today_str}.xlsx"
        
        # 컬럼 정의
        # 기존 '상세근거' 항목은 유지하되, 분석기에서 분리해 둔 상세 필드를 추가합니다.
        self.columns = [
            "학교코드", "학교명", "전화번호", "학교급", "진단상태", "미달내역",
            "교육활동참여자수", "총시간", "이수율", "훈련"
        ]

    def create_full_list(self, json_filename=None):
        """
        JSON 폴더 안에 있는 학교 리스트를 읽어서 반환만 합니다.
        """
        if json_filename is None:
            json_filename = config.SCHOOL_LIST_FILE
        
        full_path = self.json_dir / json_filename

        if not full_path.exists():
            print(f"❌ 오류: '{full_path}' 파일을 찾을 수 없습니다.")
            print(f"👉 '{json_filename}' 파일을 '{self.json_dir}' 폴더 안으로 옮겨주세요!")
            return []

        import json
        with open(full_path, "r", encoding="utf-8") as f:
            full_list = json.load(f)

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
        if self.file_name.exists():
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