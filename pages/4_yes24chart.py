import streamlit as st
import pandas as pd
from mariadb_crud import findAll
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="yes24 차트",
    page_icon="💗",
    layout="wide",
)

st.title("Yes24 주간 베스트셀러 차트")

# 1. 데이터 로드 및 전처리


@st.cache_data
def load_trend_data():
    # 모든 데이터를 가져와서 분석용으로 가공
    sql = "SELECT * FROM books"
    data = findAll(sql)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    # 데이터 타입 변환
    df[['star', 'saleNum', 'reviews', 'weekNo']] = df[[
        'star', 'saleNum', 'reviews', 'weekNo']].apply(pd.to_numeric)

    # 평점 없는 도서 처리
    df.loc[df['star'] == 0, 'star'] = np.nan

    # 카테고리 & 주차별로 그룹화 (평균 또는 합계 계산)
    # 판매수와 리뷰는 '합계(sum)', 평점은 '평균(mean)'으로 계산
    trend = df.groupby(['category', 'weekNo']).agg({
        'saleNum': 'sum',
        'reviews': 'sum',
        'star': 'mean'
    }).reset_index()

    return trend


df_trend = load_trend_data()

if not df_trend.empty:
    # 상태 관리 (슬라이더와 라디오 버튼의 값)
    weeks = sorted(df_trend['weekNo'].unique())

    # 지표 매핑용 사전
    col_map = {"총 판매수": "saleNum", "평균 평점": "star", "총 리뷰 수": "reviews"}

    # 지표 선택
    y_option = st.radio(
        "확인할 지표 선택",
        ["총 판매수", "평균 평점", "총 리뷰 수"],
        horizontal=True
    )
    # 차트 출력 영역
    chart_placeholder = st.empty()

    st.divider()

    # 주차 범위 설정 영역
    start_wk, end_wk = st.select_slider(
        '📅 조회 주차 범위 선택',
        options=weeks,
        value=(min(weeks), max(weeks))
    )

    # 필터링 및 차트 생성
    target_col = col_map[y_option]
    filtered_df = df_trend[(df_trend['weekNo'] >= start_wk)
                           & (df_trend['weekNo'] <= end_wk)]

    fig = go.Figure()
    for cat in ["국내 도서", "국외 도서"]:
        chart_data = filtered_df[filtered_df['category']
                                 == cat].sort_values('weekNo')
        fig.add_trace(go.Scatter(
            x=chart_data['weekNo'],
            y=chart_data[target_col],
            mode='lines+markers',
            name=cat,
            line=dict(dash='dash' if cat == "국외 도서" else 'solid', width=3),
            marker=dict(size=10)
        ))

    fig.update_layout(
        title=f"📊 {start_wk}주 ~ {end_wk}주 {y_option} 추이",
        xaxis_title="주차",
        yaxis_title=y_option,
        hovermode="x unified",
        height=500,
        xaxis=dict(tickmode='linear', dtick=1),
        margin=dict(t=50, b=50),
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, xanchor="center",x=0.5),
    )

    # placeholder를 사용하여 상단에 차트 주입
    chart_placeholder.plotly_chart(fig, width='stretch')

else:
    st.error("DB에서 데이터를 불러올 수 없습니다.")
