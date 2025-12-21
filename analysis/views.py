# analysis/views.py
from django.shortcuts import render
import json

# ------------------------------------------------------------------------------------------------------------------------
# 강한 2번 타자
def strong_second_view(request):
    # 1. 가상 데이터 생성 (추후 DB 연동 예정)
    # 최근 5년간 2번 타자의 평균 OPS 추이 가정
    dummy_data = {
        'years': ['2019', '2020', '2021', '2022', '2023'],
        'ops_2nd': [0.780, 0.795, 0.810, 0.825, 0.840], # 상승세 (강한 2번 트렌드 반영)
        'ops_avg': [0.750, 0.755, 0.740, 0.730, 0.735], # 리그 평균
        'top_players': [
            {'name': '김하성', 'team': 'Kiwoom', 'wRC': 145},
            {'name': 'Trout', 'team': 'LAA', 'wRC': 170},
            {'name': 'Freeman', 'team': 'LAD', 'wRC': 160},
        ]
    }
    context = {
        'data': dummy_data
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