import os
import django
import pandas as pd
import sys
import unicodedata

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analysis.models import MlbPlayerCost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_science', 'data')

def normalize_name(name):
    """ 이름 정규화 (악센트 제거, 소문자 변환 등) """
    if not isinstance(name, str):
        return ""
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii.lower().replace('.', '').strip()

def clean_currency(value):
    """ $81.00 -> 81000000 변환 """
    if pd.isna(value) or value == '':
        return 0
    if isinstance(value, str):
        clean_str = value.replace('$', '').replace(',', '')
        try:
            return int(float(clean_str) * 1_000_000)
        except ValueError:
            return 0
    elif isinstance(value, (int, float)):
        return int(value * 1_000_000)
    return 0

def import_data():
    years = range(2020, 2026) 
    types = ['batter', 'pitcher']
    
    print("🗑️ 기존 데이터 삭제 중...")
    MlbPlayerCost.objects.all().delete()

    for year in years:
        short_year = str(year)[-2:] 
        
        for p_type in types:
            salary_file = os.path.join(DATA_DIR, f'cleaned_MLB_AAV_{short_year}_{p_type}.csv')
            dollars_file = os.path.join(DATA_DIR, f'dollars_{p_type}_{year}.csv')
            
            if not os.path.exists(salary_file) or not os.path.exists(dollars_file):
                continue

            print(f"📥 처리 중: {year}년 {p_type}...")

            try:
                # 데이터 로드 및 컬럼 소문자 변환
                df_dollars = pd.read_csv(dollars_file)
                df_dollars.columns = [c.strip().lower() for c in df_dollars.columns]
                
                df_salary = pd.read_csv(salary_file)
                df_salary.columns = [c.strip().lower() for c in df_salary.columns]
                
                # Salary 매핑용 딕셔너리 생성 (이름 정규화 적용)
                salary_map = {}
                for _, row in df_salary.iterrows():
                    norm_name = normalize_name(row['name'])
                    salary_map[norm_name] = row['salary']

                batch = []
                for _, row in df_dollars.iterrows():
                    raw_name = row.get('name', '')
                    team = row.get('team', '')
                    
                    # [수정됨] WAR 컬럼 찾기 로직 개선
                    # 1. 정확히 'war'인 컬럼을 먼저 찾음 (우선순위)
                    if 'war' in df_dollars.columns:
                        war_col = 'war'
                    else:
                        # 2. 없으면 'war'가 포함된 컬럼 (예: ra9-war) - 차선책
                        war_col = next((c for c in df_dollars.columns if 'war' in c), None)
                    
                    war = row.get(war_col, 0) if war_col else 0
                    
                    # Dollars 변환
                    dollars_raw = row.get('dollars', 0)
                    dollars_val = clean_currency(dollars_raw)
                    
                    # 이름 매칭 로직
                    target_name = normalize_name(raw_name)
                    salary_val = salary_map.get(target_name)
                    
                    if salary_val is None:
                        suffixes = [' jr', ' sr', ' ii', ' iii']
                        for suffix in suffixes:
                            if target_name.endswith(suffix):
                                name_without_suffix = target_name[:-len(suffix)].strip()
                                salary_val = salary_map.get(name_without_suffix)
                                if salary_val:
                                    break
                    
                    if salary_val is None:
                        salary_val = 0

                    surplus = dollars_val - salary_val
                    
                    player = MlbPlayerCost(
                        year=year,
                        name=raw_name,
                        team=team,
                        player_type=p_type,
                        salary=salary_val,
                        war=war,
                        dollars=dollars_val,
                        surplus_value=surplus
                    )
                    batch.append(player)
                
                MlbPlayerCost.objects.bulk_create(batch)
                print(f"✅ {year} {p_type}: {len(batch)}명 저장됨")

            except Exception as e:
                print(f"❌ 에러 ({year} {p_type}): {e}")

    print("🎉 데이터 업데이트 완료!")

if __name__ == '__main__':
    import_data()