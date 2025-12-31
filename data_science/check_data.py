import pandas as pd
import os

# 파일 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '..', 'simulation', 'data', 'statcast_2025.parquet')

print(f"🔍 파일 정밀 분석 중: {file_path}")

try:
    df = pd.read_parquet(file_path)
    
    # 1. 전체 데이터 개수
    total_rows = len(df)
    print(f"\n📊 전체 데이터 개수: {total_rows:,} 개")

    # 2. 주요 컬럼 결측치(NaN/None) 확인
    # 구속(release_speed)과 구종(pitch_type)이 없는 데이터가 얼마나 되는지 봅니다.
    missing_speed = df['release_speed'].isnull().sum()
    missing_type = df['pitch_type'].isnull().sum()

    print("-" * 30)
    print(f"❌ 구속(release_speed) 누락: {missing_speed:,} 개 ({missing_speed/total_rows*100:.2f}%)")
    print(f"❌ 구종(pitch_type) 누락: {missing_type:,} 개 ({missing_type/total_rows*100:.2f}%)")
    print("-" * 30)

    # 3. 데이터가 존재하는 행만 샘플링해서 보기
    # 구속 데이터가 있는 행 중에서 랜덤으로 5개를 뽑아봅니다.
    valid_data = df.dropna(subset=['release_speed', 'pitch_type'])
    
    if not valid_data.empty:
        print("\n✨ 유효한 데이터 랜덤 샘플 (5개):")
        print(valid_data[['game_date', 'player_name', 'pitch_type', 'release_speed', 'events']].sample(5))
    else:
        print("\n🚨 경고: 유효한(구속/구종이 있는) 데이터가 하나도 없습니다!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")