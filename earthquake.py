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
# 가상의 데이터를 생성합니다. 실제 파일이 있다면 이 부분은 건너뜁니다.
import numpy as np
try:
    df_new = pd.read_csv("earthquake.csv")
except FileNotFoundError:
    # 테스트용 가상 데이터 생성 (파일이 없을 경우 대비)
    data = {
        '위도': np.random.uniform(33, 39, 1000),
        '경도': np.random.uniform(125, 130, 1000),
        '규모': np.random.uniform(1, 6, 1000),
        'cluster': np.random.choice([0, 1, 2], 1000)
    }
    df_new = pd.DataFrame(data)
    # st.warning("데이터 파일('earthquake.csv')을 찾을 수 없어 테스트용 가상 데이터를 사용합니다.")
    # 실제 환경에서는 아래 st.stop() 주석을 해제하세요.
    # st.error("데이터 파일('earthquake.csv')을 찾을 수 없습니다.")
    # st.stop()

# 위험도 사전
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}

# 군집 색상 (위성 지도에서 잘 보이도록 조정)
# 0: 빨강(위험), 1: 밝은 파랑(안전), 2: 노랑(보통)
colors = {0: '#FF0000', 1: '#00FFFF', 2: '#FFFF00'}

# [변경 포인트 1] 위험 상황 이미지 URL 정의 삭제 (필요 없음)
# danger_image_url = "..." 

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

        # [변경 포인트 2] 위험 상황 이미지 표시 코드 블록 삭제
        # if main_cluster == 0:
        #     st.image(danger_image_url, caption="위험 상황 경고", use_column_width=True)

        # [변경 포인트 3] 지도 생성: 비행기 화면 스타일(위성 지도)로 변경
        # ESRI World Imagery 위성 타일을 사용합니다.
        esri_satellite = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGS, and the GIS User Community"
        
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=6, # 비행기 뷰처럼 약간 더 멀리서 보게 조정
            tiles=esri_satellite, 
            attr=attr
        )

        # 데이터 샘플링
        df_sample = df_new.sample(min(500, len(df_new)), random_state=42)

        # 지도에 점 표시
        for i in range(len(df_sample)):

            cluster = df_sample.iloc[i]['cluster']
            scale = df_sample.iloc[i]['규모']

            folium.CircleMarker(
                location=[
                    df_sample.iloc[i]['위도'],
                    df_sample.iloc[i]['경도']
                ],
                # 규모에 따른 크기 보정 (위성지도에서 잘 보이게)
                radius=scale * 1.5, 
                color='white', # 테두리는 흰색으로 해서 구분감 줌
                weight=0.5,
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.8 # 투명도 약간 낮춤
            ).add_to(m)

        # 사용자 위치 표시 (비행기 아이콘 등으로 바꾸면 더 느낌이 삽니다)
        folium.Marker(
            location=[lat, lon],
            popup="입력 위치",
            # 아이콘을 공항/비행기 느낌으로 변경
            icon=folium.Icon(color='red', icon='plane') 
        ).add_to(m)

        # 스트림릿에 지도 출력
        st_folium(m, use_container_width=True, height=600, returned_objects=[])

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: #6c757d;'>Copyright © 2023 지방 지진 데이터 분석팀. All rights reserved.</p>", unsafe_allow_html=True)
