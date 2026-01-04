# data_science/import_pitch_data.py
import pandas as pd
import os
import sys
import django
import numpy as np
import csv

# ------------------------------------------------------------------
# Django 환경 설정
# ------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from simulation.models import PitchData
from django.db import connection  # [추가] DB 연결 제어 모듈

# [설정] CSV 필드 크기 제한 해제
csv.field_size_limit(2147483647)

def import_data():
    csv_path = os.path.join(BASE_DIR, 'simulation', 'data', 'mlb_2025.csv')
    
    print(f"🚀 데이터베이스 이관 작업 시작... (파일: {os.path.basename(csv_path)})")
    
    if not os.path.exists(csv_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        return

    # [핵심 수정] DB 연결 강제 수립
    # Django가 연결을 지연 로딩하지 않도록 명시적으로 연결을 엽니다.
    if connection.connection is None:
        connection.ensure_connection()
        print("✅ DB 연결 수립 완료")

    required_cols = [
        'player_name', 'game_date', 'p_throws', 'pitch_type',
        'release_speed', 'release_pos_x', 'release_pos_y', 'release_pos_z',
        'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az',
        'sz_top', 'sz_bot', 'pfx_x', 'pfx_z',
        'release_spin_rate', 'plate_x', 'plate_z'
    ]

    chunk_size = 10000 
    total_processed = 0
    
    try:
        with pd.read_csv(
            csv_path, 
            chunksize=chunk_size, 
            usecols=lambda c: c in required_cols,
            low_memory=False,
            on_bad_lines='skip',
            encoding='utf-8'
        ) as reader:
            
            for chunk in reader:
                chunk = chunk.replace({np.nan: None})
                
                objs = []
                for row in chunk.to_dict('records'):
                    if not row.get('player_name'): 
                        continue
                    objs.append(PitchData(**row))
                
                if objs:
                    # batch_size 유지 (안전성 확보)
                    PitchData.objects.bulk_create(objs, batch_size=999)
                    
                    total_processed += len(objs)
                    print(f"   -> {total_processed:,}개 데이터 저장 완료...")

        print("✅ 모든 데이터 저장 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_data()