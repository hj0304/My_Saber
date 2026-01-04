# data_science/build_strong_second.py
import pandas as pd
import os
import json

# --------------------------------------------------------------------------------------
# 1. 경로 설정
# --------------------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) # 프로젝트 루트
DATA_DIR = os.path.join(BASE_DIR, 'analysis', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'strong_second_data.json')

TARGET_YEARS = list(range(2016, 2026))

def build_strong_second_data():
    print("⚾ 강한 2번 타자 데이터 생성 시작...")
    
    mlb_data = {}
    mlb_teams_set = set()
    avg_data = {y: {} for y in TARGET_YEARS}

    suffixes = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 
                5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th'}
    
    # 데이터 처리 로직 (views.py에서 가져옴)
    for folder_year in TARGET_YEARS:
        print(f"   -> {folder_year}년 데이터 처리 중...")
        for order, suffix in suffixes.items():
            filename = f"Splits Leaderboard Data Batting {suffix}.csv"
            stats_path = os.path.join(DATA_DIR, 'batting_order', str(folder_year), filename)
            freq_path = os.path.join(DATA_DIR, 'frequency', str(folder_year), filename)

            if not os.path.exists(stats_path) or not os.path.exists(freq_path):
                continue

            try:
                # (1) 데이터 로드
                df_stats = pd.read_csv(stats_path, encoding='utf-8-sig')
                df_stats.columns = df_stats.columns.str.strip()

                df_freq = pd.read_csv(freq_path, encoding='utf-8-sig')
                df_freq.columns = df_freq.columns.str.strip()

                # (2) 전처리
                for col in ['OPS', 'wRC+', 'PA', 'Season']:
                    if col in df_stats.columns:
                        df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce').fillna(0)
                
                for col in ['PA', 'OPS', 'wRC+']:
                    if col in df_freq.columns:
                        df_freq[col] = pd.to_numeric(df_freq[col], errors='coerce').fillna(0)

                # (3) 대표 선수 추출
                if not df_freq.empty and 'PA' in df_freq.columns:
                    df_freq = df_freq.sort_values(by='PA', ascending=False)
                    df_rep = df_freq.drop_duplicates(subset=['Tm'], keep='first').copy()
                    
                    rename_map = {'Name': 'PlayerName', 'PA': 'PlayerPA', 'OPS': 'PlayerOPS', 'wRC+': 'PlayerWRC'}
                    rename_cols = {k: v for k, v in rename_map.items() if k in df_rep.columns}
                    df_rep = df_rep.rename(columns=rename_cols)
                else:
                    df_rep = pd.DataFrame(columns=['Tm', 'PlayerName', 'PlayerPA', 'PlayerOPS', 'PlayerWRC'])

                # (4) 병합
                player_cols = [c for c in ['Tm', 'PlayerName', 'PlayerPA', 'PlayerOPS', 'PlayerWRC'] if c in df_rep.columns]
                merged_df = pd.merge(df_stats, df_rep[player_cols], on='Tm', how='left')

                # (5) 딕셔너리 구조화
                for _, row in merged_df.iterrows():
                    team = row['Tm']
                    real_year = int(row['Season'])
                    
                    if real_year not in TARGET_YEARS: continue

                    if team not in mlb_data: mlb_data[team] = {}
                    if real_year not in mlb_data[team]: mlb_data[team][real_year] = {}
                    
                    mlb_data[team][real_year][order] = {
                        'team_ops': round(row['OPS'], 3),
                        'team_wrc': round(row['wRC+'], 1) if 'wRC+' in row else 0.0,
                        'team_pa': int(row['PA']) if 'PA' in row else 0,
                        'player_name': row['PlayerName'] if pd.notna(row.get('PlayerName')) else "Unknown",
                        'player_pa': int(row['PlayerPA']) if pd.notna(row.get('PlayerPA')) else 0,
                        'player_ops': round(row['PlayerOPS'], 3) if pd.notna(row.get('PlayerOPS')) else 0.000,
                        'player_wrc': round(row['PlayerWRC'], 1) if pd.notna(row.get('PlayerWRC')) else 0.0
                    }
                    mlb_teams_set.add(team)

                # (6) 평균 데이터
                if not df_stats.empty:
                    current_file_year = int(df_stats['Season'].mode()[0])
                    if current_file_year in TARGET_YEARS:
                        if order not in avg_data[current_file_year]:
                            avg_data[current_file_year][order] = {}
                        
                        avg_data[current_file_year][order] = {
                            'ops': round(df_stats['OPS'].mean(), 3),
                            'wrc_plus': round(df_stats['wRC+'].mean(), 1) if 'wRC+' in df_stats.columns else 0.0
                        }

            except Exception as e:
                print(f"[Error] {folder_year}년 {order}순 처리 중: {e}")

    # (7) 결과 저장
    output_data = {
        'mlb_teams_data': mlb_data,
        'mlb_avg': avg_data,
        'mlb_team_list': sorted(list(mlb_teams_set))
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ 데이터 생성 완료: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_strong_second_data()