import pandas as pd
import glob
import os
import json

# 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, '..', 'simulation', 'data')
output_file = os.path.join(base_dir, 'dashboard_summary.json')

def generate_dashboard_data():
    print("🚀 데이터 요약 작업 시작 (10년 치 데이터 스캔 중...)")
    
    # 결과 담을 딕셔너리
    summary = {
        "total_pitches": 0,
        "years": {},
        "pitch_types": {},
        "top_pitchers": {}
    }
    
    # 모든 파케이 파일 찾기
    files = sorted(glob.glob(os.path.join(data_dir, "statcast_*.parquet")))
    
    if not files:
        print("❌ 데이터 파일이 없습니다.")
        return

    # 메모리 터짐 방지를 위해 파일 하나씩 열어서 집계 (Chunk processing)
    all_pitch_types = pd.Series(dtype='int')
    all_pitchers = pd.Series(dtype='int')

    for file in files:
        filename = os.path.basename(file)
        print(f"   Reading {filename}...")
        
        df = pd.read_parquet(file, columns=['game_date', 'pitch_type', 'player_name'])
        
        # 1. 연도 추출 및 개수 세기
        year = str(pd.to_datetime(df['game_date'].iloc[0]).year)
        count = len(df)
        summary['years'][year] = count
        summary['total_pitches'] += count
        
        # 2. 구종 집계 누적
        type_counts = df['pitch_type'].value_counts()
        all_pitch_types = all_pitch_types.add(type_counts, fill_value=0)
        
        # 3. 투수별 집계 누적
        pitcher_counts = df['player_name'].value_counts()
        all_pitchers = all_pitchers.add(pitcher_counts, fill_value=0)

    # 집계 데이터 정리 (정수형 변환)
    # 구종 Top 10
    summary['pitch_types'] = all_pitch_types.sort_values(ascending=False).head(10).astype(int).to_dict()
    
    # 투수 Top 10
    summary['top_pitchers'] = all_pitchers.sort_values(ascending=False).head(10).astype(int).to_dict()

    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
        
    print("-" * 30)
    print(f"✅ 요약 완료! 총 투구 수: {summary['total_pitches']:,} 개")
    print(f"💾 요약 파일 저장됨: {output_file}")

if __name__ == "__main__":
    generate_dashboard_data()