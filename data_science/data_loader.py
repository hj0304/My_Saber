import pandas as pd
import glob
import os

class StatcastLoader:
    def __init__(self, data_dir='../simulation/data'):
        # 현재 파일 위치 기준으로 데이터 폴더 절대 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, data_dir)
        
    def load_all_years(self):
        """폴더 내의 모든 statcast_xxxx.parquet 파일을 읽어서 하나로 합칩니다."""
        # glob 패턴을 써서 statcast_*.parquet 파일 리스트를 가져옵니다.
        file_pattern = os.path.join(self.data_dir, "statcast_*.parquet")
        files = glob.glob(file_pattern)
        
        if not files:
            print("❌ 데이터 파일을 찾을 수 없습니다!")
            return None

        print(f"📂 총 {len(files)}개의 연도별 데이터 파일을 찾았습니다.")
        
        df_list = []
        for file in sorted(files):
            print(f"   - 로딩 중: {os.path.basename(file)} ...")
            # 필요한 컬럼만 로드하면 속도가 훨씬 빠릅니다 (메모리 절약)
            # 일단 전체를 로드하고 싶다면 columns=None 으로 두세요.
            df = pd.read_parquet(file)
            df_list.append(df)
            
        # 하나로 병합
        print("🔄 데이터 병합 중...")
        full_df = pd.concat(df_list, ignore_index=True)
        
        print(f"✅ 통합 완료! 총 데이터: {len(full_df):,} 개")
        return full_df

# --- 실행 테스트 ---
if __name__ == "__main__":
    loader = StatcastLoader()
    df = loader.load_all_years()
    
    if df is not None:
        # 연도별 데이터 개수 확인 (검증)
        print("\n📊 연도별 데이터 개수 확인:")
        # game_date가 문자열이면 날짜형으로 변환 후 연도 추출
        df['year'] = pd.to_datetime(df['game_date']).dt.year
        print(df['year'].value_counts().sort_index())