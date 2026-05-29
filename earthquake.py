import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="지방 지진 데이터 분석 시스템",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 불러오기
try:
    df_new = pd.read_csv("earthquake.csv")
except FileNotFoundError:
    st.error("데이터 파일('earthquake.csv')을 찾을 수 없습니다.")
    st.stop()

# 위험도 사전
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}

# 군집 색상
colors = {0: 'red', 1: 'blue', 2: 'green'}

# 위험 상황 이미지 URL
danger_image_url = "https://thumb.mt.co.kr/cdn-cgi/image/f=avif/21/2025/03/2025032816455538318_1.jpg"

# 커스텀 CSS 정의
st.markdown("""
<style>
/* 전체 페이지 배경색 및 글꼴 */
body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 사이드바 스타일 */
.sidebar .sidebar-content {
    background-color: #343a40;
    color: #f8f9fa;
}
.sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
    color: #f8f9fa;
}
.sidebar .sidebar-content .stButton>button {
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    border: none;
    padding: 10px 20px;
}
.sidebar .sidebar-content .stButton>button:hover {
    background-color: #0069d9;
}

/* 메인 화면 스타일 */
.stTitle {
    color: #0056b3;
}
.stSubheader {
    color: #495057;
}

/* 결과 출력 스타일 */
.stAlert {
    border-radius: 10px;
}
.stAlert .stAlertContent {
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# 사이드바 구성
st.sidebar.title("🌍 지방 지진 데이터 분석")
st.sidebar.markdown("---")
st.sidebar.subheader("위치 입력")
lat = st.sidebar.number_input("위도 (Latitude)", value=37.5, format="%.4f")
lon = st.sidebar.number_input("경도 (Longitude)", value=127.0, format="%.4f")
st.sidebar.markdown("---")
analysis_button = st.sidebar.button("위험도 분석 실행")

# 메인 화면
st.title("지방 지진 데이터 분석 시스템")
st.markdown("---")
st.write("본 시스템은 입력하신 위도와 경도 주변의 과거 지진 데이터를 분석하여 지진 위험도를 평가합니다. 공식적인 지진 예보가 아니며, 참고 자료로 활용하시기 바랍니다.")

# 버튼 클릭 시
if analysis_button:

    # 주변 지진 찾기
    near_df = df_new[
        (df_new['위도'] >= lat - 5) &
        (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) &
        (df_new['경도'] <= lon + 5)
    ]

    # 주변 데이터가 없는 경우
    if len(near_df) == 0:
        st.sidebar.warning("해당 위치 주변에 충분한 지진 데이터가 없습니다. 분석 범위를 넓혀보세요.")

    else:
        # 군집 비율 계산
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)

        # 가장 많은 군집
        main_cluster = cluster_ratio.idxmax()

        # 위험도 출력 (세련되게)
        danger_level = risk_dict[main_cluster]
        if danger_level == '높음':
            st.error(f"⚠️ **예상 위험도: 높음**")
        elif danger_level == '중간':
            st.warning(f"⚠️ **예상 위험도: 중간**")
        else:
            st.success(f"✅ **예상 위험도: 낮음**")

        # 위험 상황 이미지 표시
        if main_cluster == 0:
            st.image(danger_image_url, caption="위험 상황 경고", use_column_width=True)

        # 지도 생성
        m = folium.Map(location=[lat, lon], zoom_start=4, tiles="CartoDB positron")

        # 데이터 샘플링
        df_sample = df_new.sample(500, random_state=42)

        # 지도에 점 표시
        for i in range(len(df_sample)):

            cluster = df_sample.iloc[i]['cluster']

            folium.CircleMarker(
                location=[
                    df_sample.iloc[i]['위도'],
                    df_sample.iloc[i]['경도']
                ],
                radius=df_sample.iloc[i]['규모'],
                color=colors[cluster],
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.7
            ).add_to(m)

        # 사용자 위치 표시
        folium.Marker(
            location=[lat, lon],
            popup="입력 위치",
            icon=folium.Icon(color='black', icon='star')
        ).add_to(m)

        # 스트림릿에 지도 출력
        st_folium(m, use_container_width=True, returned_objects=[])

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: #6c757d;'>Copyright © 2023 지방 지진 데이터 분석팀. All rights reserved.</p>", unsafe_allow_html=True)