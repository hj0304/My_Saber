import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stat Stabilization Point", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # data_science 폴더 위치 찾기 (상대경로 주의)
    csv_path = os.path.join(base_dir, '..', '..', 'data_science', 'stabilization_results.csv')
    return pd.read_csv(csv_path)

try:
    df = load_data()
    
    st.title("📈 스탯 안정화 시점 (Stabilization Points)")
    st.markdown("""
    **"이 기록을 믿어도 될까?"** 10년 치 데이터를 기반으로, 각 스탯이 '진짜 실력'을 반영하기 시작하는 **샘플 사이즈(PA)**를 분석했습니다.  
    일반적으로 **상관계수 0.7 (R² 0.5)**을 넘으면 안정화되었다고 봅니다.
    """)

    st.divider()

    # 그래프 그리기
    fig = px.line(df, x='pa_threshold', y='correlation', color='stat', markers=True,
                  title="타석 수(PA)에 따른 지표별 신뢰도 변화",
                  labels={'pa_threshold': '타석 수 (PA)', 'correlation': '신뢰도 (Correlation)'})
    
    # 기준선 (0.7) 추가
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="안정화 기준 (0.7)")
    
    # y축 범위 설정 (0 ~ 1)
    fig.update_yaxes(range=[0, 1])
    
    st.plotly_chart(fig, use_container_width=True)

    # 상세 분석 텍스트
    st.subheader("💡 분석 결과 해석")
    
    # 스탯별로 0.7 넘는 지점 찾기
    stats = df['stat'].unique()
    for stat in stats:
        stat_df = df[df['stat'] == stat]
        # 0.7을 처음 넘는 행 찾기
        stabilized = stat_df[stat_df['correlation'] >= 0.7]
        
        if not stabilized.empty:
            point = stabilized.iloc[0]['pa_threshold']
            st.success(f"**{stat}**: 약 **{point} 타석**부터 신뢰할 수 있습니다.")
        else:
            st.warning(f"**{stat}**: 분석 범위(600타석) 내에서 아직 0.7에 도달하지 않았습니다. (더 많은 타석 필요)")

    st.markdown("---")
    st.caption("Method: Split-Half Reliability with Spearman-Brown Prophecy Formula")

except FileNotFoundError:
    st.error("결과 파일이 없습니다. 'data_science/calc_stabilization.py'를 먼저 실행해주세요.")