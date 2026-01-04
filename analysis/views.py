# analysis/views.py
from django.shortcuts import render
import json
import random
# Sample size를 위한
import math
import pandas as pd
import os
# 가성비 선수 지표를 위한
from .models import MlbPlayerCost
from django.db.models import Max


# ------------------------------------------------------------------------------------------------------------------------
# 강한 2번 타자
def strong_second_view(request):
    target_years = list(range(2016, 2026))
    
    # KBO 가상 데이터용
    kbo_teams = ["KIA", "Samsung", "LG", "Doosan", "KT", "SSG", "Lotte", "Hanwha", "NC", "Kiwoom"]
    kbo_players = ["김도영", "구자욱", "홍창기", "양의지", "최정", "로하스", "에레디아", "박건우", "강백호", "노시환"]

    def load_mlb_real_data():
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'analysis', 'data')
        
        mlb_data = {}
        mlb_teams_set = set()
        avg_data = {y: {} for y in target_years}

        suffixes = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 
                    5: '5th', 6: '6th', 7: '7th', 8: '8th', 9: '9th'}
        
        print("--- MLB 데이터 로드 시작 (데이터 분리 적용) ---")

        for folder_year in target_years:
            for order, suffix in suffixes.items():
                filename = f"Splits Leaderboard Data Batting {suffix}.csv"
                stats_path = os.path.join(data_dir, 'batting_order', str(folder_year), filename)
                freq_path = os.path.join(data_dir, 'frequency', str(folder_year), filename)

                if not os.path.exists(stats_path) or not os.path.exists(freq_path):
                    continue

                try:
                    # (1) 팀 성적 데이터 로드
                    df_stats = pd.read_csv(stats_path, encoding='utf-8-sig')
                    df_stats.columns = df_stats.columns.str.strip()

                    # (2) 선수 빈도 데이터 로드
                    df_freq = pd.read_csv(freq_path, encoding='utf-8-sig')
                    df_freq.columns = df_freq.columns.str.strip()

                    # (3) 데이터 전처리 (숫자 변환)
                    # 팀 데이터 숫자 변환
                    for col in ['OPS', 'wRC+', 'PA', 'Season']:
                        if col in df_stats.columns:
                            df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce').fillna(0)
                    
                    # 선수 데이터 숫자 변환
                    for col in ['PA', 'OPS', 'wRC+']:
                        if col in df_freq.columns:
                            df_freq[col] = pd.to_numeric(df_freq[col], errors='coerce').fillna(0)

                    # (4) 대표 선수 추출 (선수 개인 성적 포함)
                    if not df_freq.empty and 'PA' in df_freq.columns:
                        df_freq = df_freq.sort_values(by='PA', ascending=False)
                        # 팀별 최다 타석 선수 1명 추출
                        df_rep = df_freq.drop_duplicates(subset=['Tm'], keep='first').copy()
                        
                        # [핵심] 선수 개인 성적 컬럼명 변경 (팀 성적과 구분하기 위해 'Player' 접두사 붙임)
                        # Name -> PlayerName, PA -> PlayerPA, OPS -> PlayerOPS, wRC+ -> PlayerWRC
                        rename_map = {
                            'Name': 'PlayerName',
                            'PA': 'PlayerPA',
                            'OPS': 'PlayerOPS',
                            'wRC+': 'PlayerWRC'
                        }
                        # 존재하는 컬럼만 변경
                        rename_cols = {k: v for k, v in rename_map.items() if k in df_rep.columns}
                        df_rep = df_rep.rename(columns=rename_cols)
                    else:
                        df_rep = pd.DataFrame(columns=['Tm', 'PlayerName', 'PlayerPA', 'PlayerOPS', 'PlayerWRC'])

                    # (5) 데이터 병합 (Team 기준)
                    # df_stats(팀 성적) + df_rep(선수 성적)
                    # 필요한 컬럼만 선택해서 병합
                    player_cols = [c for c in ['Tm', 'PlayerName', 'PlayerPA', 'PlayerOPS', 'PlayerWRC'] if c in df_rep.columns]
                    merged_df = pd.merge(df_stats, df_rep[player_cols], on='Tm', how='left')

                    # (6) 딕셔너리 저장
                    for _, row in merged_df.iterrows():
                        team = row['Tm']
                        real_year = int(row['Season']) # 파일 내부의 실제 연도 사용
                        
                        if real_year not in target_years: continue

                        if team not in mlb_data: mlb_data[team] = {}
                        if real_year not in mlb_data[team]: mlb_data[team][real_year] = {}
                        
                        # 데이터 할당
                        mlb_data[team][real_year][order] = {
                            # A. 팀 성적 (좌측 그래프용)
                            'team_ops': round(row['OPS'], 3),
                            'team_wrc': round(row['wRC+'], 1) if 'wRC+' in row else 0.0,
                            'team_pa': int(row['PA']) if 'PA' in row else 0,
                            
                            # B. 선수 성적 (우측 박스용)
                            'player_name': row['PlayerName'] if pd.notna(row.get('PlayerName')) else "Unknown",
                            'player_pa': int(row['PlayerPA']) if pd.notna(row.get('PlayerPA')) else 0,
                            'player_ops': round(row['PlayerOPS'], 3) if pd.notna(row.get('PlayerOPS')) else 0.000,
                            'player_wrc': round(row['PlayerWRC'], 1) if pd.notna(row.get('PlayerWRC')) else 0.0
                        }
                        mlb_teams_set.add(team)

                    # (7) 리그 평균 계산
                    if not df_stats.empty:
                        current_file_year = int(df_stats['Season'].mode()[0])
                        if current_file_year in target_years:
                            if order not in avg_data[current_file_year]:
                                avg_data[current_file_year][order] = {}
                            
                            avg_data[current_file_year][order] = {
                                'ops': round(df_stats['OPS'].mean(), 3),
                                'wrc_plus': round(df_stats['wRC+'].mean(), 1) if 'wRC+' in df_stats.columns else 0.0
                            }

                except Exception as e:
                    print(f"[Error] {folder_year}년 {order}번 타순 처리 중 오류: {e}")

        print(f"--- 로드 완료: {len(mlb_teams_set)}개 팀 ---")
        return mlb_data, avg_data, sorted(list(mlb_teams_set))

    # KBO 더미 데이터 (구조 맞춰줌)
    def generate_kbo_dummy_data(teams, player_names):
        league_data = {} 
        avg_data = {}    
        for year in target_years:
            avg_data[year] = {}
            for order in range(1, 10):
                avg_data[year][order] = {'ops': 0.750}
        
        for team in teams:
            league_data[team] = {}
            for year in target_years:
                league_data[team][year] = {}
                for order in range(1, 10):
                    league_data[team][year][order] = {
                        'team_ops': round(0.750 + random.uniform(-0.1, 0.1), 3),
                        'team_wrc': round(100 + random.uniform(-20, 20), 1),
                        'team_pa': random.randint(600, 700),
                        'player_name': random.choice(player_names),
                        'player_pa': random.randint(400, 600),
                        'player_ops': round(0.800 + random.uniform(-0.1, 0.1), 3),
                        'player_wrc': round(110 + random.uniform(-20, 20), 1)
                    }
        return league_data, avg_data

    mlb_teams_data, mlb_avg, mlb_team_list = load_mlb_real_data()
    kbo_teams_data, kbo_avg = generate_kbo_dummy_data(kbo_teams, kbo_players)

    all_data = {
        'kbo': {'teams_data': kbo_teams_data, 'avg_data': kbo_avg, 'team_list': kbo_teams},
        'mlb': {'teams_data': mlb_teams_data, 'avg_data': mlb_avg, 'team_list': mlb_team_list}
    }

    context = {
        'years': json.dumps(target_years),
        'all_data': json.dumps(all_data)
    }
    
    return render(request, 'analysis/strong_second.html', context)

# ------------------------------------------------------------------------------------------------------------------------
# 선발 투수 메타
def pitcher_meta_view(request):
    # --- 가상 데이터 생성 로직 (추후 실제 DB 연동) ---
    # 가정: 기본 승률 50%
    # 1. 실점이 적을수록 승률 대폭 상승
    # 2. 이닝을 많이 먹을수록(불펜 소모 감소) 승률 소폭 상승
    
    matrix_data = []
    
    for ip in range(1, 10): # 1이닝 ~ 9이닝
        for runs in range(0, 10): # 0실점 ~ 9실점
            
            # 승률 계산 알고리즘 (예시)
            base_win_rate = 50
            run_impact = (4.5 - runs) * 8  # 평균 4.5점 기준, 1점 줄일 때마다 승률 8% 변동
            inning_impact = (ip - 6) * 1.5 # 6이닝 기준, 1이닝 더 던지면 1.5% 이득 (불펜 아낌)
            
            final_win_rate = base_win_rate + run_impact + inning_impact
            
            # 0~100 사이로 보정
            final_win_rate = max(0, min(99.9, final_win_rate))
            
            matrix_data.append({
                'ip': ip,
                'runs': runs,
                'win_rate': round(final_win_rate, 1)
            })

    # 프론트엔드(JavaScript)에서 쓰기 편하게 JSON 형태로 변환
    context = {
        'matrix_json': json.dumps(matrix_data)
    }
    
    return render(request, 'analysis/pitcher_meta.html', context)

# ------------------------------------------------------------------------------------------------------------------------
# 선발 투수 메타, 기대승리 그래프
def pitcher_meta_view(request):
    # 1. 계산기용 데이터 (넓은 범위: 1~9이닝, 0~10실점)
    # 기존 로직 유지
    calculator_data = []
    for ip in range(1, 10):
        for runs in range(0, 11):
            # 가상 승률 로직 (단순화)
            # 기본 50% + (9이닝 기준 이닝당 2% 가산) - (실점당 8% 감산)
            win_rate = 50 + ((ip - 5) * 2) - (runs * 8)
            win_rate = max(0, min(99.9, win_rate)) # 0~99.9% 제한
            
            calculator_data.append({
                'ip': ip,
                'runs': runs,
                'win_rate': round(win_rate, 1)
            })

    # 2. 히트맵용 데이터 (특정 범위: 3~9이닝, 0~7실점)
    # 템플릿에서 그리기 편하게 2차원 리스트 구조로 만듭니다.
    heatmap_rows = []
    
    for ip in range(9, 2, -1): # 9이닝부터 3이닝까지 역순 (표의 위쪽이 9이닝이 되도록)
        row_data = {'ip': ip, 'cols': []}
        for runs in range(0, 8): # 0실점 ~ 7실점
            
            # 위와 동일한 로직 사용 (나중엔 실제 데이터 쿼리로 대체)
            win_rate = 50 + ((ip - 5) * 2) - (runs * 8)
            win_rate = max(0, min(99.9, win_rate))
            
            # 색상 투명도 계산 (승률이 높을수록 진하게)
            # 50%를 기준으로 0~1 사이의 alpha값 생성
            # 간단하게 승률 자체를 불투명도로 사용 (0.0 ~ 1.0)
            opacity = win_rate / 100
            
            row_data['cols'].append({
                'runs': runs,
                'win_rate': round(win_rate, 1),
                'opacity': opacity
            })
        heatmap_rows.append(row_data)

    context = {
        'matrix_json': json.dumps(calculator_data), # JS 계산기용
        'heatmap_rows': heatmap_rows                # HTML 표 그리기용
    }
    
    return render(request, 'analysis/pitcher_meta.html', context)

# ------------------------------------------------------------------------------------------------------------------------
# 불펜투수 지표
def relief_metrics_view(request):
    # 1. 파일 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kbo_csv_path = os.path.join(base_dir, 'analysis', 'data', 'RP_stats_KBO.csv')
    mlb_csv_path = os.path.join(base_dir, 'analysis', 'data', 'RP_stats_MLB.csv')
    
    # 2. 데이터 처리 함수
    def process_data(file_path, start_year, end_year, top_n=30):
        data_by_year = {}
        valid_years = []

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}") # 디버깅용
            return {}, []

        try:
            # 한글이 포함된 CSV일 수 있으므로 encoding 주의 (utf-8-sig 또는 cp949)
            # 여기서는 일반적인 utf-8로 시도합니다. 에러 시 encoding='cp949'로 변경해보세요.
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # 컬럼명 공백 제거 (혹시 모를 오류 방지)
            df.columns = df.columns.str.strip()
            
            # 연도 데이터 정수형 변환 및 필터링
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
            df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
            
            valid_years = sorted(df['Year'].unique().tolist())
            
            for year in valid_years:
                year_df = df[df['Year'] == year].copy()
                
                # WPA 기준 내림차순 정렬 후 상위 N명 추출
                year_df = year_df.sort_values(by='WPA', ascending=False).head(top_n)
                
                # 프론트엔드 전송용 리스트 변환
                players = []
                for _, row in year_df.iterrows():
                    players.append({
                        'name': row['Name'],
                        'team': row['Team'],
                        'wpa': round(float(row['WPA']), 2),
                        # gmLI가 없는 경우 0.0 처리
                        'gmli': round(float(row['gmLI']), 2) if 'gmLI' in row else 0.0,
                        'year': year
                    })
                data_by_year[year] = players
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
        return data_by_year, valid_years

    # 3. 데이터 로드 (KBO: 2019~, MLB: 2016~, Top n)
    kbo_data, kbo_years = process_data(kbo_csv_path, 2019, 2025, 10)
    mlb_data, mlb_years = process_data(mlb_csv_path, 2016, 2025, 30)

    all_data = {
        'kbo': kbo_data,
        'mlb': mlb_data
    }

    context = {
        # 각 리그별 가능한 연도 리스트를 따로 전달
        'kbo_years': json.dumps(kbo_years),
        'mlb_years': json.dumps(mlb_years),
        'all_data': json.dumps(all_data)
    }
    
    return render(request, 'analysis/relief_metrics.html', context)

# ------------------------------------------------------------------------------------------------------------------------
# 가성비 선수 지표 (dollars와 Cost per WAR)
def cost_effectiveness_view(request):
    selected_year = int(request.GET.get('year', 2025))
    selected_type = request.GET.get('type', 'batter')

    # 1. 전체 데이터 가져오기 (차트용)
    queryset = MlbPlayerCost.objects.filter(year=selected_year, player_type=selected_type)
    
    # 차트 데이터 (Scatter Plot: x=연봉, y=가치)
    scatter_data = []
    for p in queryset:
        # 연봉이나 가치가 있는 선수만
        if p.salary > 0 or p.dollars > 0:
            scatter_data.append({
                'x': p.salary,
                'y': p.dollars,
                'name': p.name,
                'team': p.team,
                'surplus': p.surplus_value
            })

    # 2. Top 30 리스트 & 비율 계산용 Max값 추출
    # Dollars 기준
    top_dollars = queryset.order_by('-dollars')[:30]
    max_dollars = top_dollars[0].dollars if top_dollars else 1
    
    # 리스트에 비율(percentage) 속성 추가 (템플릿에서 바 그래프용)
    top_dollars_list = []
    for p in top_dollars:
        p.pct = (p.dollars / max_dollars) * 100 if max_dollars else 0
        top_dollars_list.append(p)

    # Surplus 기준
    top_surplus = queryset.order_by('-surplus_value')[:30]
    max_surplus = top_surplus[0].surplus_value if top_surplus else 1
    
    top_surplus_list = []
    for p in top_surplus:
        p.pct = (p.surplus_value / max_surplus) * 100 if max_surplus else 0
        top_surplus_list.append(p)

    years = list(range(2020, 2026))

    context = {
        'years': years,
        'selected_year': selected_year,
        'selected_type': selected_type,
        'top_dollars': top_dollars_list,
        'top_surplus': top_surplus_list,
        'scatter_data': json.dumps(scatter_data), # JSON으로 변환해서 전달
    }
    
    return render(request, 'analysis/cost_effectiveness.html', context)

# ------------------------------------------------------------------------------------------------------------------------
# 샘플 사이즈와 신뢰도
def sample_size_view(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 파일명 v2로 변경 확인!
    csv_path = os.path.join(base_dir, 'data_science', 'stabilization_results_v2.csv')

    context = {}
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # JSON 변환
        context['chart_data'] = json.dumps(df.to_dict(orient='records'))
        context['data_exists'] = True
    else:
        context['data_exists'] = False

    return render(request, 'analysis/sample_size.html', context)
    # 차트 데이터 생성 함수
    def generate_chart_data(stat_list, max_range):
        datasets = []
        x_values = list(range(0, max_range + 1, 50)) # 0 ~ Max까지 50단위

        for stat in stat_list:
            data_points = []
            k = stat['threshold']
            
            for x in x_values:
                if x == 0:
                    y = 0
                else:
                    # 신뢰도 곡선 시뮬레이션 (x=k일 때 0.7(R^2=0.5) 수준 도달 가정)
                    # 수식: Reliability = x / (x + k * 0.4) -> 단순화된 모델
                    # 설명: 표본(x)이 임계값(k)만큼 쌓이면 꽤 높은 신뢰도를 보임
                    ratio = x / k
                    # 시각적으로 예쁜 Log-like Curve
                    reliability = 1 - (1 / (1 + 0.8 * ratio + 0.2 * (ratio**2)))
                    data_points.append(round(min(reliability, 1.0), 3))
            
            datasets.append({
                'label': stat['name'],
                'data': data_points,
                'borderColor': stat['color'],
                'threshold': stat['threshold']
            })
        return x_values, datasets

    # 각각 데이터 생성
    # 타자는 600 PA, 투수는 600 BF 정도까지 보여줌
    x_batter, data_batter = generate_chart_data(batter_stats, 700)
    x_pitcher, data_pitcher = generate_chart_data(pitcher_stats, 700)

    context = {
        # JSON으로 변환하여 템플릿에 전달
        'batter_data': json.dumps({'labels': x_batter, 'datasets': data_batter}),
        'pitcher_data': json.dumps({'labels': x_pitcher, 'datasets': data_pitcher})
    }
    
    return render(request, 'analysis/sample_size.html', context)