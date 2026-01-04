# data_science/inspect_data.py
import pandas as pd
import os

# 확인하고 싶은 연도 설정 (문제가 있는 연도 중 하나 선택)
TARGET_YEAR = 2025  

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'simulation', 'data', f'statcast_{TARGET_YEAR}.parquet')

def inspect_parquet():
    if not os.path.exists(DATA_PATH):
        print(f"❌ 파일이 없습니다: {DATA_PATH}")
        return

    print(f"🕵️‍♂️ {TARGET_YEAR}년 데이터 정밀 분석 중...")
    
    try:
        # 1. 데이터 로드
        df = pd.read_parquet(DATA_PATH)
        print(f"✅ 파일 로드 성공! (총 행 개수: {len(df):,} rows)")
        
        # 2. 날짜 범위 확인 (가장 의심되는 부분)
        if 'game_date' in df.columns:
            dates = df['game_date'].unique()
            print(f"\n📅 데이터 날짜 범위:")
            print(f"   - 시작일: {min(dates)}")
            print(f"   - 종료일: {max(dates)}")
            print(f"   - 수집된 날짜 수: {len(dates)}일")
        else:
            print("\n⚠️ 'game_date' 컬럼이 없습니다.")

        # 3. 게임 수 확인
        if 'game_pk' in df.columns:
            games = df['game_pk'].nunique()
            print(f"\n⚾ 고유 경기(Game PK) 수: {games} 경기 (정상 범위: 약 2,400 경기)")
        
        # 4. 게임 타입 확인 (정규시즌 'R' 필터링 문제인지 확인)
        if 'game_type' in df.columns:
            print(f"\n🏷️ 게임 타입 분포:\n{df['game_type'].value_counts()}")
        
        # 5. 이닝 데이터 샘플 (로직 문제인지 확인)
        if 'inning_topbot' in df.columns:
            print(f"\n🔄 이닝 표시 샘플: {df['inning_topbot'].unique()[:5]}")

    except Exception as e:
        print(f"❌ 데이터 읽기 오류 발생: {e}")

if __name__ == "__main__":
    inspect_parquet()