import pandas as pd
import os

def convert_excel_to_clean_csv(filename):
    # 1. 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(base_dir, 'data_science', 'raw_data')
    output_dir = os.path.join(base_dir, 'data_science', 'data')
    
    input_path = os.path.join(raw_data_dir, filename)
    output_filename = f"cleaned_{os.path.splitext(filename)[0]}.csv"
    output_path = os.path.join(output_dir, output_filename)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_path):
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        return

    print(f"🔄 엑셀 변환 시작 (5컬럼): {filename}")
    
    try:
        df_raw = pd.read_excel(input_path, header=None)
        lines = df_raw.iloc[:, 0].dropna().astype(str).tolist()
    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return

    data = []
    current_rank = 1
    last_salary_index = -1 
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 1. 팀/포지션 라인 식별 (쉼표가 있고 문자가 섞여있음)
        has_comma = ',' in line
        has_letters = any(c.isalpha() for c in line)
        
        if has_comma and has_letters:
            # 따옴표 제거 후 쉼표로 분리
            raw_info = line.replace('"', '').strip()
            parts = raw_info.split(',')
            
            # [Team] & [Pos] 분리 로직
            team = parts[0].strip()
            if len(parts) > 1:
                pos = parts[1].strip() # 쉼표 뒤쪽은 포지션
            else:
                pos = "Unknown"      # 혹시 포지션이 없는 경우 대비

            # [Name]: 윗줄
            if i - 1 >= 0:
                name = lines[i-1].strip()
            else:
                name = "Unknown"
            
            # [Salary]: 아랫줄
            salary = 0
            if i + 1 < len(lines):
                salary_str = lines[i+1].replace(',', '').replace('"', '').replace('.0', '')
                if salary_str.isdigit():
                    salary = int(salary_str)
            
            # [Rank]: 전전줄 확인
            if i - 2 >= 0:
                potential_rank = lines[i-2].strip().replace('.0', '')
                if potential_rank.isdigit() and (i - 2) != last_salary_index:
                    current_rank = int(potential_rank)
            else:
                if lines[i-2].strip().replace('.0', '').isdigit():
                     current_rank = int(lines[i-2].strip().replace('.0', ''))

            # 데이터 추가 (5개 컬럼)
            data.append({
                'rank': current_rank,
                'name': name,
                'team': team,
                'pos': pos,     # 추가된 컬럼
                'salary': salary
            })
            
            last_salary_index = i + 1
            i += 2
        else:
            i += 1

    if not data:
        print("⚠️ 변환된 데이터가 없습니다.")
        return

    # DataFrame 생성 및 컬럼 순서 지정
    df_result = pd.DataFrame(data)
    df_result = df_result[['rank', 'name', 'team', 'pos', 'salary']]
    
    df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ 변환 완료! {len(df_result)}명 저장됨.")
    print(f"📂 저장 위치: {output_path}")

if __name__ == "__main__":
    target_file = 'MLB_AAV_25_pitcher.xlsx' #연도(20~25)와 투타(batter or pitcher) 잘 살피고 실행하기. # MLB_AAV_25_pitcher.xlsx
    convert_excel_to_clean_csv(target_file)