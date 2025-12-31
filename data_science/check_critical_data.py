import pandas as pd
import os

# 파일 경로
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '..', 'simulation', 'data', 'statcast_2025.parquet')

print("🕵️‍♂️ '진짜' 데이터 무결성 검사 중...\n")

df = pd.read_parquet(file_path)

# 1. 타석 결과(events)가 있는 데이터만 뽑아봅니다. (이게 OPS 계산의 핵심 데이터)
# events가 None인 것은(볼, 스트라이크 등) 타율 계산에 안 쓰니까 일단 제외합니다.
valid_at_bats = df[df['events'].notnull()]

print(f"✅ 타석 결과가 나온 데이터(타수/사사구 등): {len(valid_at_bats):,} 개")

# 2. 여기서 치명적인 결측치가 있는지 확인합니다.
# "결과(events)는 있는데, 타자 이름이나 날짜가 없다?" -> 이건 진짜 문제입니다.
critical_missing = valid_at_bats[valid_at_bats['player_name'].isnull() | valid_at_bats['game_date'].isnull()]

if len(critical_missing) > 0:
    print(f"🚨 비상! 치명적인 데이터 누락 발견: {len(critical_missing)} 개")
    print(critical_missing[['game_date', 'player_name', 'events']])
else:
    print("👍 완벽합니다! 타석 결과가 있는 모든 데이터에 날짜와 선수 이름이 꽉 차 있습니다.")

# 3. events 컬럼에 어떤 값들이 들어있는지 확인 (이상한 값이 섞여있나 체크)
print("\n📊 타석 결과값 종류 (상위 10개):")
print(valid_at_bats['events'].value_counts().head(10))

# 4. (추가) OPS 계산할 때 홈런, 안타 등이 잘 섞여 있는지 비율 확인
print("\n📈 데이터 밸런스 체크:")
total_ab = len(valid_at_bats)
hr_count = len(valid_at_bats[valid_at_bats['events'] == 'home_run'])
so_count = len(valid_at_bats[valid_at_bats['events'] == 'strikeout'])

print(f" - 전체 타석 결과: {total_ab:,} 개")
print(f" - 홈런: {hr_count:,} 개 (약 {hr_count/total_ab*100:.1f}%)")
print(f" - 삼진: {so_count:,} 개 (약 {so_count/total_ab*100:.1f}%)")