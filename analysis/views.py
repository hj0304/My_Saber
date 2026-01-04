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
    
    # 1. KBO 가상 데이터 (유지)
    kbo_teams = ["KIA", "Samsung", "LG", "Doosan", "KT", "SSG", "Lotte", "Hanwha", "NC", "Kiwoom"]
    kbo_players = ["김도영", "구자욱", "홍창기", "양의지", "최정", "로하스", "에레디아", "박건우", "강백호", "노시환"]
    
    def generate_kbo_dummy_data(teams, player_names):
        # ... (기존 코드와 동일) ...
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

    kbo_teams_data, kbo_avg = generate_kbo_dummy_data(kbo_teams, kbo_players)

    # 2. MLB 데이터 로드 (JSON 방식 - 개선됨)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'analysis', 'data', 'strong_second_data.json')
    
    mlb_teams_data = {}
    mlb_avg = {}
    mlb_team_list = []

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mlb_teams_data = data.get('mlb_teams_data', {})
                mlb_avg = data.get('mlb_avg', {})
                mlb_team_list = data.get('mlb_team_list', [])
        except Exception as e:
            print(f"Error loading strong second JSON: {e}")
    else:
        print("Warning: strong_second_data.json not found. Run build_strong_second.py first.")

    # 3. Context 전달
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
# 선발 투수 메타 (실제 데이터 반영 버전)
def pitcher_meta_view(request):
    # 1. JSON 파일 경로
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'analysis', 'data', 'pitcher_meta_matrix.json')
    
    real_data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                real_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            real_data = []

    # 2. 데이터 매핑
    data_map = {}
    for d in real_data:
        data_map[(d['ip'], d['runs'])] = {
            'win_rate': d['win_rate'],
            'count': d.get('sample_size', 0)
        }

    # 3. 히트맵 데이터 생성
    heatmap_rows = []
    for ip in range(9, 2, -1): # 9 ~ 3이닝
        row_data = {'ip': ip, 'cols': []}
        for runs in range(0, 8): # 0 ~ 7실점
            
            data = data_map.get((ip, runs))
            
            if data is None:
                # 데이터 없음 (N/A)
                row_data['cols'].append({
                    'win_rate': None,
                    'count': 0,
                    'color_type': 'none', # 색상 타입 없음
                    'opacity': 0
                })
            else:
                win_rate = data['win_rate']
                count = data['count']
                
                # [수정] 컬러 스케일 로직 (Red-Blue Diverging)
                # 50%를 기준으로 거리 계산 (0.0 ~ 1.0)
                # 예: 50% -> 0.0 (회색), 100% -> 1.0 (진한 파랑), 0% -> 1.0 (진한 빨강)
                intensity = abs(win_rate - 50) * 2 / 100.0
                
                # 최소 가시성 확보 (너무 연하지 않게 기본 0.1 추가)
                opacity = 0.1 + (intensity * 0.9)
                
                # 색상 결정
                if win_rate >= 50:
                    color_type = 'blue' # 승리 확률 높음
                else:
                    color_type = 'red'  # 승리 확률 낮음 (패배 확률 높음)

                row_data['cols'].append({
                    'runs': runs,
                    'win_rate': win_rate,
                    'count': count,
                    'color_type': color_type, # 템플릿에서 class 분기용
                    'opacity': opacity
                })
                
        heatmap_rows.append(row_data)

    context = {
        'matrix_json': json.dumps(real_data),
        'heatmap_rows': heatmap_rows
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