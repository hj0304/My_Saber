import pandas as pd
import numpy as np
import os
import sys

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from data_loader import StatcastLoader

def get_slg_value(event):
    """장타율 계산을 위한 루타 수 매핑"""
    if event == 'single': return 1
    elif event == 'double': return 2
    elif event == 'triple': return 3
    elif event == 'home_run': return 4
    return 0

def calculate_correlations():
    loader = StatcastLoader()
    df = loader.load_all_years()
    
    if df is None: return

    print("🚀 고급 스탯 신뢰도 분석 시작 (MLB Statcast)...")

    # 1. 기본 전처리
    df['year'] = pd.to_datetime(df['game_date']).dt.year
    df['player_season_id'] = df['player_name'] + "_" + df['year'].astype(str)
    
    # 반분 신뢰도용 그룹 (홀수/짝수)
    df['group'] = np.where(df.index % 2 == 0, 'A', 'B')

    # ---------------------------------------------------------
    # 2. 파생 변수 생성 (Statcast -> 야구 지표 매핑)
    # ---------------------------------------------------------
    
    # (1) 스윙/컨택 관련 (description 컬럼 활용)
    swings = ['foul', 'foul_bunt', 'foul_tip', 'hit_into_play', 'swinging_strike', 'swinging_strike_blocked', 'missed_bunt']
    contacts = ['foul', 'foul_bunt', 'foul_tip', 'hit_into_play']
    
    df['is_swing'] = df['description'].isin(swings).astype(int)
    df['is_contact'] = df['description'].isin(contacts).astype(int) # 분모는 Swing일 때만 써야 함
    
    # (2) 타구질 관련 (bb_type 활용)
    df['is_gb'] = (df['bb_type'] == 'ground_ball').astype(int)
    df['is_ld'] = (df['bb_type'] == 'line_drive').astype(int)
    df['is_fb'] = (df['bb_type'] == 'fly_ball').astype(int)
    df['is_popup'] = (df['bb_type'] == 'popup').astype(int)
    
    # (3) 결과 관련 (events 활용)
    df['is_k'] = df['events'].isin(['strikeout', 'strikeout_double_play']).astype(int)
    df['is_bb'] = df['events'].isin(['walk']).astype(int)
    df['is_1b'] = (df['events'] == 'single').astype(int)
    df['is_hr'] = (df['events'] == 'home_run').astype(int)
    
    # (4) AVG, OBP, SLG용
    df['is_hit'] = df['events'].isin(['single', 'double', 'triple', 'home_run']).astype(int)
    df['is_onbase'] = df['events'].isin(['single', 'double', 'triple', 'home_run', 'walk', 'hit_by_pitch']).astype(int)
    df['slg_val'] = df['events'].apply(get_slg_value) # 0, 1, 2, 3, 4

    # ---------------------------------------------------------
    # 3. 분석할 스탯 정의 (카테고리 분류)
    # ---------------------------------------------------------
    # 형식: {'표시이름': ('컬럼명', '조건필터_컬럼', '분모_설명')}
    # 조건필터가 None이면 전체 데이터 대상
    
    stats_map = {
        'Offense': {
            'Swing%': ('is_swing', None), # 전체 투구 중 스윙 비율
            'Contact%': ('is_contact', 'is_swing'), # 스윙 중 컨택 비율
            'Strikeout Rate': ('is_k', 'events_exist'), # 타석당 삼진
            'Walk Rate': ('is_bb', 'events_exist'),     # 타석당 볼넷
            'Home Run Rate': ('is_hr', 'events_exist'), # 타석당 홈런
            'AVG': ('is_hit', 'ab_flag'), # 타수당 안타 (약식: events 있으면 타수로 가정)
            'OBP': ('is_onbase', 'events_exist'),
            'SLG': ('slg_val', 'ab_flag'),
            'ISO': ('slg_val', 'ab_flag'), # ISO는 SLG - AVG 이지만 여기선 SLG랑 비슷하게 추이 봄
            'Line Drive%': ('is_ld', 'is_batted'), # 타구 중 라인드라이브
            'Ground Ball%': ('is_gb', 'is_batted'),
            'Fly Ball%': ('is_fb', 'is_batted'),
            'Popup%': ('is_popup', 'is_batted'),
        },
        'Pitching': {
            # 투수 입장은 타자와 동일한 로직이지만 'Player'가 투수여야 함 (나중에 그룹핑할 때 처리)
            'K/PA': ('is_k', 'events_exist'),
            'BB/PA': ('is_bb', 'events_exist'),
            'HR/PA': ('is_hr', 'events_exist'),
            'GB%': ('is_gb', 'is_batted'),
            'FB%': ('is_fb', 'is_batted'),
        }
    }

    # 필터용 플래그 생성
    df['events_exist'] = df['events'].notnull() # 타석 결과가 있는 경우 (PA)
    df['is_batted'] = df['bb_type'].notnull()   # 타구가 발생한 경우
    df['ab_flag'] = df['events'].isin(['single','double','triple','home_run','strikeout','strikeout_double_play','field_out']) # 대략적 AB

    results = []
    
    # 구간 설정 (50 ~ 600)
    thresholds = range(50, 601, 50)

    # --- 분석 루프 ---
    for category, metrics in stats_map.items():
        # 투수/타자 기준 설정
        if category == 'Pitching':
            id_col = 'pitcher_season_id' # 투수 기준 (추가 필요)
            # 투수 ID 생성
            df['pitcher_season_id'] = df['player_name'] + "(P)_" + df['year'].astype(str)
        else:
            id_col = 'player_season_id' # 타자 기준

        for stat_name, (val_col, filter_col) in metrics.items():
            print(f"   📊 [{category}] {stat_name} 분석 중...")
            
            # 필터링 (분모가 되는 상황만 추출)
            if filter_col:
                target_df = df[df[filter_col] == True]
            else:
                target_df = df # 전체 투구 대상

            for threshold in thresholds:
                # 1. 샘플 사이즈 충족하는 선수 찾기
                counts = target_df.groupby(id_col).size()
                valid_players = counts[counts >= threshold].index
                
                if len(valid_players) < 50: continue # 선수 너무 적으면 패스

                sample = target_df[target_df[id_col].isin(valid_players)]

                # 2. 반분 신뢰도 계산
                grouped = sample.groupby([id_col, 'group'])[val_col].mean().unstack()
                grouped = grouped.dropna()

                if len(grouped) > 30:
                    r = grouped['A'].corr(grouped['B'])
                    if pd.isna(r): continue
                    
                    r_corrected = (2 * r) / (1 + r) # 스피어만-브라운 보정
                    
                    results.append({
                        'category': category,
                        'stat': stat_name,
                        'pa': threshold,
                        'correlation': round(r_corrected, 3)
                    })

    # 저장
    output_path = os.path.join(current_dir, 'stabilization_results_v2.csv')
    pd.DataFrame(results).to_csv(output_path, index=False)
    print("✅ 모든 분석 완료! 저장됨:", output_path)

if __name__ == "__main__":
    calculate_correlations()