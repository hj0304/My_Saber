# simulation/views.py
from django.shortcuts import render
import pandas as pd
import json
import os
from django.conf import settings

def pitch_tunnel_view(request):
    # [수정] CSV 파일 경로 변경 (simulation/data/ 폴더 내부 참조)
    csv_path = os.path.join(settings.BASE_DIR, 'simulation', 'data', 'yamamoto_pitching_data.csv')
    
    pitch_data = []
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        
        required_cols = [
            'player_name', 'p_throws',
            'pitch_type', 'release_speed', 
            'release_pos_x', 'release_pos_y', 'release_pos_z',
            'vx0', 'vy0', 'vz0', 
            'ax', 'ay', 'az',
            'sz_top', 'sz_bot',
            'pfx_x', 'pfx_z',
            'release_spin_rate', 
            'plate_x', 'plate_z'
        ]
        
        # 컬럼 존재 여부 확인 후 필터링
        available_cols = [c for c in required_cols if c in df.columns]
        df_clean = df[available_cols].dropna().sample(n=min(len(df), 300))
        
        pitch_data = df_clean.to_dict(orient='records')
    else:
        print(f"Error: CSV file not found at {csv_path}") # 디버깅용 로그
    
    context = {
        'pitch_data': json.dumps(pitch_data)
    }
    
    return render(request, 'simulation/pitch_tunnel.html', context)