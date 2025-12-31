import os
import glob
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# ==========================================================
# 1. 경로 설정 (collect_data.py와 동일한 로직 적용)
# ==========================================================
# 현재 파일(analyze_reliability.py)의 절대 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 상위 폴더(..)로 이동 후 simulation/data/ 로 진입
DATA_DIR = os.path.join(BASE_DIR, '..', 'simulation', 'data')

# 경로 정규화 (OS 호환성 확보)
DATA_DIR = os.path.normpath(DATA_DIR)
# ==========================================================


def load_all_data(data_dir):
    """
    DATA_DIR 내의 모든 statcast_*.parquet 파일을 로드하여 하나로 합칩니다.
    """
    print(f"📂 데이터 로딩 경로: {data_dir}")
    all_files = glob.glob(os.path.join(data_dir, "statcast_*.parquet"))
    
    if not all_files:
        print("⚠️ 데이터 파일이 없습니다. collect_data.py를 먼저 실행해 주세요.")
        return None

    print(f"   -> 총 {len(all_files)}개의 파일을 발견했습니다. 병합을 시작합니다...")
    
    # 리스트 컴프리헨션으로 로드 후 concat (메모리 효율 및 속도 최적화)
    df_list = [pd.read_parquet(f) for f in all_files]
    full_df = pd.concat(df_list, ignore_index=True)
    
    print(f"📊 총 {len(full_df):,}개 행(Rows) 로드 완료.")
    return full_df


def add_pa_count(df):
    """
    타자별 시즌 누적 타석 번호(PA Count)를 생성합니다.
    분석의 핵심인 '짝홀법'을 적용하기 위해 필수적인 단계입니다.
    """
    print("🔢 PA Count(타석 번호) 생성 및 정렬 중...")
    
    # 1. 정렬: 날짜 -> 경기ID -> 경기 내 타석 번호 순
    # (데이터가 뒤죽박죽이면 순서가 꼬이므로 필수)
    df = df.sort_values(by=['game_date', 'game_pk', 'at_bat_number'])
    
    # 2. 유효 타석 필터링
    # events 컬럼이 비어있지 않은 행(타석 결과가 나온 행)만 추출
    # (투구 단위 데이터에서 타석 단위 데이터로 변환)
    pa_df = df[df['events'].notnull()].copy()
    
    # 3. 그룹핑 및 순번 매기기
    # 연도별(game_year), 타자별(batter)로 그룹지어 1부터 번호 부여
    pa_df['pa_count_season'] = pa_df.groupby(['game_year', 'batter']).cumcount() + 1
    
    print("✅ PA Count 생성 완료.")
    return pa_df


def calculate_reliability_stat(pa_df, stat_col, min_pa=50):
    """
    특정 스탯(stat_col)에 대한 신뢰도(Split-Half Reliability)를 계산합니다.
    
    :param pa_df: PA Count가 포함된 타석 데이터프레임
    :param stat_col: 분석할 스탯 컬럼명 (예: 'launch_speed', 'is_homerun' 등)
    :param min_pa: 분석 대상에 포함시킬 최소 타석 수 (노이즈 제거용)
    """
    print(f"🧪 스탯 분석 중: {stat_col} ...")
    
    # 1. 최소 타석 이상 들어선 선수만 필터링
    # 선수별 총 타석 수 계산
    player_counts = pa_df.groupby(['game_year', 'batter']).size()
    valid_players = player_counts[player_counts >= min_pa].index
    
    # 인덱스 매칭을 위해 set_index 사용 (속도 향상)
    pa_df_indexed = pa_df.set_index(['game_year', 'batter'])
    target_df = pa_df_indexed.loc[pa_df_indexed.index.isin(valid_players)].reset_index()
    
    if target_df.empty:
        print("   -> 조건에 맞는 선수가 없습니다.")
        return 0.0

    # 2. 짝수/홀수 타석 분리
    odd_df = target_df[target_df['pa_count_season'] % 2 != 0]
    even_df = target_df[target_df['pa_count_season'] % 2 == 0]
    
    # 3. 선수별 평균 스탯 계산
    # (groupby 후 mean()을 하면 선수별 해당 스탯의 평균/비율이 나옴)
    odd_stats = odd_df.groupby(['game_year', 'batter'])[stat_col].mean()
    even_stats = even_df.groupby(['game_year', 'batter'])[stat_col].mean()
    
    # 4. 데이터 짝 맞추기 (홀/짝 모두 기록이 있는 선수만)
    # inner join으로 교집합만 남김
    combined = pd.concat([odd_stats, even_stats], axis=1, join='inner')
    combined.columns = ['odd', 'even']
    
    # 5. 피어슨 상관계수 계산 (r)
    if len(combined) < 10:
        print("   -> 표본이 너무 적어 상관계수를 계산할 수 없습니다.")
        return 0.0
        
    r, p_value = pearsonr(combined['odd'], combined['even'])
    
    # 6. Spearman-Brown 공식으로 보정 (샘플 길이가 절반이 되었으므로)
    r_corrected = (2 * r) / (1 + r)
    
    print(f"   -> 분석 대상: {len(combined)}명 (시즌)")
    print(f"   -> 상관계수(r): {r:.3f} / 보정값: {r_corrected:.3f}")
    
    return r_corrected


# ==========================================================
# 실행부 (Main)
# ==========================================================
if __name__ == "__main__":
    # 1. 데이터 로드
    full_df = load_all_data(DATA_DIR)
    
    if full_df is not None:
        # 2. 전처리: PA Count 생성
        # (메모리 절약을 위해 필요한 컬럼만 선택해서 넘길 수도 있음)
        pa_df = add_pa_count(full_df)
        
        # 3. 분석 예시
        print("\n[ 분석 결과 예시 ]")
        
        # (예시 1) 타구 속도 (Launch Speed) 신뢰도
        # 타구 속도가 있는 타석만 남김
        ls_df = pa_df.dropna(subset=['launch_speed'])
        calculate_reliability_stat(ls_df, 'launch_speed', min_pa=50)
        
        # (예시 2) 홈런율 (HR Rate) 신뢰도
        # 'events'가 'home_run'이면 1, 아니면 0인 컬럼 생성
        pa_df['is_homerun'] = pa_df['events'].apply(lambda x: 1 if x == 'home_run' else 0)
        calculate_reliability_stat(pa_df, 'is_homerun', min_pa=100) # 홈런은 희귀해서 PA 기준을 높임
        
        print("\n✅ 모든 분석 완료.")