import streamlit as st
import json
import pandas as pd
import os
import plotly.express as px # 그래프 그리는 라이브러리

# 페이지 기본 설정
st.set_page_config(page_title="Sabermetrics Dashboard", layout="wide")

# 데이터 로드 함수
@st.cache_data # 데이터를 캐싱해서 속도 향상
def load_summary():
    # data_science 폴더에 있는 json 파일을 읽어옴
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', 'data_science', 'dashboard_summary.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# --- 메인 화면 시작 ---
try:
    data = load_summary()

    st.title("⚾ 2016-2025 MLB Statcast Data Overview")
    st.markdown("### 내가 수집한 데이터의 규모(Sample Size)를 확인합니다.")

    # 1. 핵심 지표 (Metric)
    total = data['total_pitches']
    st.metric(label="총 수집된 투구 데이터 (Total Pitches)", value=f"{total:,} 개")

    st.divider() # 구분선

    # 2. 연도별 데이터 분포 (Bar Chart)
    st.subheader("📅 연도별 데이터 수집 현황")
    
    # 딕셔너리를 데이터프레임으로 변환
    df_years = pd.DataFrame(list(data['years'].items()), columns=['Year', 'Count'])
    df_years = df_years.sort_values('Year')
    
    # 그래프 그리기
    fig_years = px.bar(df_years, x='Year', y='Count', text_auto=',', 
                       title="연도별 투구 수 (2020년 단축 시즌 확인)", color='Count')
    st.plotly_chart(fig_years, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # 3. 가장 많이 던져진 구종 Top 10
        st.subheader("🎯 구종 분포 (Top 10)")
        df_types = pd.DataFrame(list(data['pitch_types'].items()), columns=['Pitch Type', 'Count'])
        fig_types = px.pie(df_types, values='Count', names='Pitch Type', hole=0.4)
        st.plotly_chart(fig_types, use_container_width=True)

    with col2:
        # 4. 투구 수 많은 투수 Top 10
        st.subheader("💪 철완 투수 (Top 10)")
        df_pitchers = pd.DataFrame(list(data['top_pitchers'].items()), columns=['Player', 'Count'])
        fig_pitchers = px.bar(df_pitchers, x='Count', y='Player', orientation='h', 
                              text_auto=',', title="누적 투구 수 상위 10명")
        # 보기 좋게 순서 뒤집기
        fig_pitchers.update_layout(yaxis={'categoryorder':'total ascending'}) 
        st.plotly_chart(fig_pitchers, use_container_width=True)

except FileNotFoundError:
    st.error("🚨 요약 데이터 파일이 없습니다! 'generate_summary.py'를 먼저 실행해주세요.")