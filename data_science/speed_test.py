import pandas as pd
import numpy as np
import time
import os

# 더미 데이터 생성 (약 50만 행)
print("📦 데이터 생성 중...")
df = pd.DataFrame(np.random.randint(0, 100, size=(500000, 10)), columns=[f'col_{i}' for i in range(10)])

# 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'test.csv')
parquet_path = os.path.join(base_dir, 'test.parquet')

print("🏁 속도 대결 시작!\n")

# 1. CSV 저장 테스트
start_time = time.time()
df.to_csv(csv_path, index=False)
csv_time = time.time() - start_time
print(f"🐢 CSV 저장 시간: {csv_time:.4f} 초")

# 2. Parquet 저장 테스트
start_time = time.time()
df.to_parquet(parquet_path)
parquet_time = time.time() - start_time
print(f"🚀 Parquet 저장 시간: {parquet_time:.4f} 초")

# 결과 비교
print("-" * 30)
if parquet_time < csv_time:
    print(f"🏆 Parquet가 {csv_time / parquet_time:.1f}배 더 빠릅니다!")
else:
    print("CSV가 더 빠릅니다 (이럴 리가 없는데?)")

# 파일 크기 비교
csv_size = os.path.getsize(csv_path) / (1024 * 1024)
parquet_size = os.path.getsize(parquet_path) / (1024 * 1024)

print(f"\n💾 파일 크기 비교:")
print(f" - CSV: {csv_size:.2f} MB")
print(f" - Parquet: {parquet_size:.2f} MB (약 {csv_size/parquet_size:.1f}배 압축됨)")

# 테스트 파일 삭제 (청소)
os.remove(csv_path)
os.remove(parquet_path)