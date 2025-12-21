# analysis/views.py
from django.shortcuts import render
import json
import random

# ------------------------------------------------------------------------------------------------------------------------
# 강한 2번 타자
def strong_second_view(request):
    # 1. MLB 팀 목록
    mlb_teams = [
        "ARI", "ATL", "BAL", "BOS", "CHC", "CWS", "CIN", "CLE", "COL", "DET",
        "HOU", "KC", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
        "PHI", "PIT", "SD", "SF", "SEA", "STL", "TB", "TEX", "TOR", "WSH"
    ]
    
    # 2. 연도 목록
    years = list(range(2016, 2026)) # 2016 ~ 2025
    
    # 3. 데이터 구조 생성 (가상 데이터)
    # 실제로는 DB에서 가져와야 할 데이터 구조입니다.
    # 구조: data[팀][연도][타순] = { ops: 0.888, top_player: "Player Name" }
    
    all_data = {}
    league_avg_data = {} # 리그 평균 (연도별, 타순별)

    # (1) 리그 평균 데이터 생성
    for year in years:
        league_avg_data[year] = {}
        for order in range(1, 10):
            # 2~5번 타순은 OPS가 높게, 하위 타선은 낮게 나오도록 랜덤 조정
            base_ops = 0.750 if order in [2, 3, 4, 5] else 0.650
            league_avg_data[year][order] = round(base_ops + random.uniform(-0.05, 0.05), 3)

    # (2) 팀별 데이터 생성
    player_names = ["Ohtani", "Judge", "Betts", "Freeman", "Trout", "Harper", "Soto", "Acuna", "Witt Jr.", "Henderson"]
    
    for team in mlb_teams:
        all_data[team] = {}
        for year in years:
            all_data[team][year] = {}
            for order in range(1, 10):
                # 리그 평균을 기준으로 약간의 편차를 둠
                avg = league_avg_data[year][order]
                team_ops = round(avg + random.uniform(-0.10, 0.10), 3)
                
                # 가상 선수 이름
                top_player = f"{random.choice(player_names)} ({team})"
                
                all_data[team][year][order] = {
                    'ops': team_ops,
                    'player_name': top_player,
                    'games': random.randint(100, 162) # 출장 경기 수
                }

    context = {
        'mlb_teams': json.dumps(mlb_teams),
        'years': json.dumps(years),
        'all_data': json.dumps(all_data),         # 팀별 상세 데이터
        'league_avg': json.dumps(league_avg_data) # 리그 평균 데이터
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