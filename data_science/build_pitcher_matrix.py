# data_science/build_pitcher_matrix.py
import pandas as pd
import numpy as np
import os
import json

# --------------------------------------------------------------------------------------
# 1. 경로 및 설정
# --------------------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) # 프로젝트 루트

# 데이터 경로: simulation/data/statcast_{year}.parquet
DATA_DIR = os.path.join(BASE_DIR, 'simulation', 'data')

# 결과 저장 경로: analysis/data/pitcher_meta_matrix.json
OUTPUT_DIR = os.path.join(BASE_DIR, 'analysis', 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'pitcher_meta_matrix.json')

TARGET_YEARS = range(2016, 2026)

# --------------------------------------------------------------------------------------
# 2. 헬퍼 함수
# --------------------------------------------------------------------------------------
def get_event_outs(event):
    """Statcast 이벤트 문자열을 아웃 카운트로 변환"""
    if pd.isna(event): return 0
    if 'triple_play' in event: return 3
    if 'double_play' in event or 'grounded_into_double_play' in event: return 2
    
    out_events = [
        'strikeout', 'field_out', 'force_out', 'sac_fly', 'sac_bunt', 
        'fielders_choice', 'fielders_choice_out', 'strikeout_double_play',
        'caught_stealing_2b', 'caught_stealing_3b', 'caught_stealing_home',
        'pickoff_caught_stealing_2b', 'pickoff_caught_stealing_3b', 
        'pickoff_caught_stealing_home', 'batter_interference'
    ]
    if 'strikeout_double_play' in event: return 2
    if event in out_events: return 1
    return 0

# --------------------------------------------------------------------------------------
# 3. 메인 로직
# --------------------------------------------------------------------------------------
def build_matrix():
    print(f"📂 데이터 경로: {DATA_DIR}")
    print("⚾ 선발 투수 승리 확률 매트릭스 생성 시작 (2016-2025)...")
    
    all_starters_data = []

    for year in TARGET_YEARS:
        file_name = f"statcast_{year}.parquet"
        file_path = os.path.join(DATA_DIR, file_name)
        
        if not os.path.exists(file_path):
            print(f"⚠️  [Skip] {year}년 데이터 파일 없음")
            continue
            
        print(f"   -> {year}년 데이터 로드 및 분석 중...", end=" ")
        
        try:
            # [수정] 정렬을 위해 'at_bat_number', 'pitch_number' 추가
            columns = [
                'game_pk', 'game_type', 'inning', 'inning_topbot', 
                'events', 'pitcher', 'post_away_score', 'post_home_score',
                'at_bat_number', 'pitch_number'
            ]
            
            # 일부 컬럼이 없을 경우를 대비해 안전하게 읽기 (try-except 보완 필요 시 사용)
            df = pd.read_parquet(file_path, columns=columns)
            
            # 정규시즌('R') 필터링
            if 'game_type' in df.columns:
                df = df[df['game_type'] == 'R']
            
            # 게임별 그룹화
            grouped = df.groupby('game_pk')
            game_count = 0
            
            for game_pk, game in grouped:
                # [핵심 수정] 데이터를 타석/투구 순서대로 정렬 (과거 -> 미래)
                # 데이터가 역순으로 저장된 경우를 바로잡음
                if 'at_bat_number' in game.columns and 'pitch_number' in game.columns:
                    game = game.sort_values(by=['at_bat_number', 'pitch_number'], ascending=[True, True])
                
                # A. 경기 결과 확인 (이제 iloc[-1]은 진짜 경기 끝!)
                last_row = game.iloc[-1]
                final_home = last_row['post_home_score']
                final_away = last_row['post_away_score']
                
                if final_home == final_away: continue # 무승부 제외

                is_home_win = final_home > final_away

                # B. 선발 투수 식별
                top_1st = game[(game['inning'] == 1) & (game['inning_topbot'] == 'Top')]
                bot_1st = game[(game['inning'] == 1) & (game['inning_topbot'] == 'Bot')]

                # 1) 홈팀 선발 (Top 1st 수비)
                if not top_1st.empty:
                    starter_id = top_1st.iloc[0]['pitcher']
                    p_events = game[game['pitcher'] == starter_id]
                    
                    outs = p_events['events'].apply(get_event_outs).sum()
                    ip = outs / 3.0
                    runs_allowed = p_events['post_away_score'].max()
                    
                    all_starters_data.append({
                        'ip': ip,
                        'runs': int(runs_allowed),
                        'win': 1 if is_home_win else 0
                    })

                # 2) 원정팀 선발 (Bot 1st 수비)
                if not bot_1st.empty:
                    starter_id = bot_1st.iloc[0]['pitcher']
                    p_events = game[game['pitcher'] == starter_id]
                    
                    outs = p_events['events'].apply(get_event_outs).sum()
                    ip = outs / 3.0
                    runs_allowed = p_events['post_home_score'].max()
                    
                    all_starters_data.append({
                        'ip': ip,
                        'runs': int(runs_allowed),
                        'win': 0 if is_home_win else 1
                    })
                
                game_count += 1
            
            print(f"완료 ({game_count}경기)")

        except Exception as e:
            print(f"\n❌ [Error] {year}년 처리 중 오류: {e}")

    # --------------------------------------------------------------------------------------
    # 4. 집계 및 저장
    # --------------------------------------------------------------------------------------
    if not all_starters_data:
        print("❌ 분석된 데이터가 없습니다.")
        return

    print(f"\n📊 총 {len(all_starters_data):,}명의 선발 등판 데이터 분석 완료.")
    
    df_res = pd.DataFrame(all_starters_data)
    
    # IP 반올림
    df_res['ip_int'] = df_res['ip'].round().astype(int)
    
    # 이상치 제거
    df_res = df_res[(df_res['ip_int'] >= 1) & (df_res['ip_int'] <= 9)]
    df_res = df_res[(df_res['runs'] >= 0) & (df_res['runs'] <= 15)]

    # 승률 계산
    matrix = df_res.groupby(['ip_int', 'runs'])['win'].agg(['mean', 'count']).reset_index()
    
    output_data = []
    for _, row in matrix.iterrows():
        output_data.append({
            'ip': int(row['ip_int']),
            'runs': int(row['runs']),
            'win_rate': round(row['mean'] * 100, 1),
            'sample_size': int(row['count'])
        })
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"✅ 결과 파일 저장 완료: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_matrix()