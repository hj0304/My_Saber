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
    years = list(range(2016, 2026)) # 2016 ~ 2025
    
    # 1. 팀 목록 정의
    mlb_teams = [
        "ARI", "ATL", "BAL", "BOS", "CHC", "CWS", "CIN", "CLE", "COL", "DET",
        "HOU", "KC", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
        "PHI", "PIT", "SD", "SF", "SEA", "STL", "TB", "TEX", "TOR", "WSH"
    ]
    kbo_teams = [
        "KIA", "Samsung", "LG", "Doosan", "KT", "SSG", "Lotte", "Hanwha", "NC", "Kiwoom"
    ]

    # 2. 선수 이름 풀
    mlb_players = ["Ohtani", "Judge", "Betts", "Freeman", "Soto", "Acuna", "Harper", "Witt Jr.", "Henderson", "Trout"]
    kbo_players = ["김도영", "구자욱", "홍창기", "양의지", "최정", "로하스", "에레디아", "박건우", "강백호", "노시환"]

    # 3. 데이터 생성 함수 (리그별)
    def generate_league_data(teams, player_names):
        league_data = {} # 팀별 데이터
        avg_data = {}    # 리그 평균 데이터 (연도별)

        # (1) 리그 평균 생성
        for year in years:
            avg_data[year] = {}
            for order in range(1, 10):
                # 2번 타자 강세 트렌드 반영 (랜덤)
                base = 0.780 if order == 2 else 0.700
                avg_data[year][order] = round(base + random.uniform(-0.05, 0.05), 3)

        # (2) 팀별 상세 데이터 생성
        for team in teams:
            league_data[team] = {}
            for year in years:
                league_data[team][year] = {}
                for order in range(1, 10):
                    avg = avg_data[year][order]
                    league_data[team][year][order] = {
                        'ops': round(avg + random.uniform(-0.1, 0.1), 3),
                        'player_name': f"{random.choice(player_names)}",
                        'games': random.randint(80, 144)
                    }
        return league_data, avg_data

    # 4. 데이터 생성 및 구조화
    kbo_teams_data, kbo_avg = generate_league_data(kbo_teams, kbo_players)
    mlb_teams_data, mlb_avg = generate_league_data(mlb_teams, mlb_players)

    all_data = {
        'kbo': {'teams_data': kbo_teams_data, 'avg_data': kbo_avg, 'team_list': kbo_teams},
        'mlb': {'teams_data': mlb_teams_data, 'avg_data': mlb_avg, 'team_list': mlb_teams}
    }

    context = {
        'years': json.dumps(years),
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
    # 1. 설정
    years = list(range(2016, 2026)) # 2016 ~ 2025
    
    # 가상 선수 이름 풀 (랜덤 생성용)
    kbo_names = ["오승환", "김원중", "조상우", "정우영", "박영현", "서진용", "임창민", "고우석", "정해영", "이용찬", "김재윤", "문경찬", "하준영", "김태훈", "최지민"]
    mlb_names = ["Diaz", "Hader", "Clase", "Phillips", "Holmes", "Duran", "Hendriks", "Iglesias", "Pressly", "Chapman", "Bautista", "Bednar", "Romano", "Doval", "Fairbanks"]
    
    # 2. 데이터 생성 함수
    def generate_year_data(names, league_prefix):
        year_data = {}
        for year in years:
            players = []
            # 연도별로 15명의 불펜 투수 데이터 생성 (나중에 상위 10명만 자를 것임)
            for name in names:
                # WPA: -1.0 ~ 5.0 사이 랜덤
                wpa = round(random.uniform(-1.0, 5.0), 2)
                # gmLI: 0.8 ~ 2.5 사이 랜덤 (중요도)
                gmli = round(random.uniform(0.8, 2.5), 2)
                
                players.append({
                    'name': name,
                    'team': f"{league_prefix} Team", # 팀명은 임시
                    'wpa': wpa,
                    'gmli': gmli,
                    'year': year
                })
            
            # WPA 높은 순으로 정렬해둠 (선택사항, 프론트에서도 할 수 있음)
            players.sort(key=lambda x: x['wpa'], reverse=True)
            year_data[year] = players
        return year_data

    # 3. 데이터 구축
    all_data = {
        'kbo': generate_year_data(kbo_names, "KBO"),
        'mlb': generate_year_data(mlb_names, "MLB")
    }

    context = {
        'years': json.dumps(years),
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