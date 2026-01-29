import pandas as pd
import os
import json
from datetime import datetime

class ExcelManager:
    def __init__(self, file_name="안전교육_점검결과_실시간.xlsx"):
        self.file_name = file_name
        # 전화번호가 포함된 표준 컬럼 정의
        self.columns = ["학교코드", "학교명", "전화번호", "학교급", "진단상태", "미달내역", "상세근거", "점검일시"]

    def create_filtering_list(self, full_school_list_path="school_list.json"):
        """
        엑셀을 분석하여 '미달' 상태이거나 '기록이 없는(신규)' 학교만 추출합니다.
        """
        with open(full_school_list_path, "r", encoding="utf-8") as f:
            full_list = json.load(f)

        if not os.path.exists(self.file_name):
            self._save_targets(full_list)
            return full_list

        try:
            df = pd.read_excel(self.file_name, dtype={"학교코드": str})
            
            # 1. 엑셀에 이미 존재하는 '미달' 학교 코드 추출
            fail_schools = df[df["진단상태"].str.contains("미달", na=False)]["학교코드"].tolist()
            
            # 2. 엑셀에 아예 없는 '신규' 학교 코드 추출
            existing_codes = df["학교코드"].tolist()
            new_schools = [code for code in full_list if code not in existing_codes]
            
            # 3. 최종 타겟: [미달 + 신규]
            target_list = list(set(fail_schools + new_schools)) # 중복 방지를 위해 set 사용 후 리스트화
            
            self._save_targets(target_list)
            print(f"📊 필터링 완료: 미달({len(fail_schools)}) + 신규({len(new_schools)}) = 총 {len(target_list)}개 수집 필요")
            return target_list
            
        except Exception as e:
            print(f"⚠️ 필터링 중 오류 발생: {e}")
            self._save_targets(full_list)
            return full_list

    def save_all_at_once(self, refined_results):
        """
        [신규 기능] 메모리에 저장된 정제 데이터 리스트를 엑셀에 일괄 저장합니다.
        기존 데이터와 합치고 중복된 학교코드는 최신 정보로 덮어씁니다.
        """
        if not refined_results:
            print("⚠️ 저장할 데이터가 없습니다.")
            return

        # 1. 기존 데이터 불러오기
        if os.path.exists(self.file_name):
            df_existing = pd.read_excel(self.file_name, dtype={"학교코드": str})
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. 새 데이터에 점검일시 추가
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        for item in refined_results:
            item["점검일시"] = current_time

        df_new = pd.DataFrame(refined_results)

        # 3. 데이터 통합 (중복된 학교코드는 새 데이터(keep='last')로 유지)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["학교코드"], keep="last")

        # 4. 최종 저장
        try:
            # 정의된 컬럼 순서대로 정렬하여 저장
            df_combined = df_combined[self.columns]
            df_combined.to_excel(self.file_name, index=False)
            print(f"✅ 엑셀 저장 완료: {self.file_name} (총 {len(df_combined)}건)")
        except PermissionError:
            print(f"❌ 저장 실패: {self.file_name} 파일이 열려 있습니다. 닫고 다시 실행하세요.")

    def _save_targets(self, target_list):
        """수집 대상 학교 코드만 별도 JSON으로 저장"""
        with open("filtering_list.json", "w", encoding="utf-8") as f:
            json.dump(target_list, f, ensure_ascii=False, indent=4)
        print("✅ 차기 수집 대상 명단(filtering_list.json) 저장 완료")

# 테스트 실행부
if __name__ == "__main__":
    em = ExcelManager()
    em.create_filtering_list()