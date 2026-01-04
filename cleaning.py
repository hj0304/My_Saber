import pandas as pd

# 1. 파일 불러오기
df = pd.read_csv('RP_stats_KBO.csv')

# 2. 모든 값이 비어있는(NaN) 행 제거 (공백 행 삭제)
df_cleaned = df.dropna(how='all')

# 3. 인덱스(행 번호)를 0부터 다시 매기기
df_cleaned = df_cleaned.reset_index(drop=True)

# 한글 깨짐 방지를 위해 'utf-8-sig' 인코딩을 사용하여 저장
df_cleaned.to_csv('RP_stats_KBO_cleaned_utf8sig.csv', index=False, encoding='utf-8-sig')

print("정리 완료! 'RP_stats_KBO_cleaned.csv' 파일이 생성되었습니다.")