import os
import time
import pandas as pd
from pybaseball import statcast
import calendar
from datetime import date
import sys

# ==========================================================
# 1. 경로 설정
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'simulation', 'data')
DATA_DIR = os.path.normpath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)
# ==========================================================

def collect_data_by_year(target_year):
    print(f"📂 데이터 저장 경로: {DATA_DIR}")
    print(f"🎯 [Target] {target_year}년 데이터 수집 시작 (무결성 최우선 모드)")
    print("   -> 정책: 모든 기간 에러 발생 시 3회 재시도 후 실패하면 즉시 종료(STOP).")
    print("   -> 건너뛰는(SKIP) 날짜는 없습니다.")
    
    yearly_dfs = []
    
    # 3월 ~ 11월
    for month in range(3, 12):
        _, last_day = calendar.monthrange(target_year, month)
        print(f"\n📅 {target_year}년 {month}월 데이터 수집 중...")
        
        for day in range(1, last_day + 1):
            date_str = f"{target_year}-{month:02d}-{day:02d}"
            
            # 미래 날짜는 중단
            if date_str > str(date.today()):
                break
            
            # === 재시도(Retry) 로직 (최대 3회) ===
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    # 데이터 요청
                    df = statcast(start_dt=date_str, end_dt=date_str)
                    
                    # 데이터 없음 (경기 없는 날) -> 정상 상황
                    if df is None or df.empty:
                        print(".", end="", flush=True)
                        success = True
                        break

                    # 정규시즌('R') 필터링
                    if 'game_type' in df.columns:
                        df = df[df['game_type'] == 'R']
                    
                    if not df.empty:
                        yearly_dfs.append(df)
                        print("O", end="", flush=True)
                    else:
                        print(".", end="", flush=True) # 정규시즌 아님
                    
                    success = True
                    break # 성공 시 재시도 루프 탈출
                    
                except Exception as e:
                    # 실패 시 잠시 대기 후 재시도
                    if attempt < max_retries - 1:
                        time.sleep(2) 
                        continue
                    else:
                        # 3번 다 실패함
                        print(f"\n❌ [ERROR] {date_str} 3회 시도 실패: {e}")
            
            # === 3번 다 실패했을 때 처리 (무조건 STOP) ===
            if not success:
                print(f"\n🛑 [STOP] {date_str} 데이터 수집 실패!")
                print("   -> 건너뛰지 않고 프로그램을 종료합니다.")
                print("   -> 원인을 확인하고 해결 후 다시 실행해주세요.")
                sys.exit(1)
                
            # 서버 차단 방지 딜레이
            time.sleep(0.5)

    # ==========================================================
    # 저장
    # ==========================================================
    print("\n\n🧩 데이터 병합 및 저장 중...")
    
    if yearly_dfs:
        full_df = pd.concat(yearly_dfs, ignore_index=True)
        file_name = f"statcast_{target_year}.parquet"
        file_path = os.path.join(DATA_DIR, file_name)
        full_df.to_parquet(file_path, index=False)
        print(f"✅ {target_year}년 저장 완료! (총 {len(full_df):,}행)")
    else:
        print(f"⚠️ {target_year}년 데이터 없음.")

if __name__ == "__main__":
    TARGET_YEAR = 2025
    collect_data_by_year(TARGET_YEAR)