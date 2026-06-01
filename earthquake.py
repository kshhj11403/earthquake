import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="지방 지진 데이터 분석 시스템",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 불러오기 (원본 로직 완벽 유지)
try:
    df_new = pd.read_csv("earthquake.csv")
except FileNotFoundError:
    st.error("데이터 파일('earthquake.csv')을 찾을 수 없습니다.")
    st.stop()

# 위험도 사전
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}

# 군집 색상 (지진 속보 모니터 화면에서 잘 보이도록 형광 톤으로 매칭)
colors = {0: '#FF3333', 1: '#00FFFF', 2: '#FFFF00'}

# [UI 변경] 전체 인터페이스를 재난 통제실/속보 화면처럼 정갈한 다크 모드로 변경
st.markdown("""
<style>
/* 전체 화면 배경 및 글꼴 */
.stApp {
    background-color: #111217 !important;
}
body {
    background-color: #111217;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1, h2, h3, p, span, label {
    color: #ffffff !important;
}

/* 사이드바 스타일 (재난 제어판 느낌) */
[data-testid="stSidebar"] {
    background-color: #1e2029 !important;
    border-right: 1px solid #2d313f;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(135deg, #cc0000, #ff3333) !important;
    color: white !important;
    border-radius: 4px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    letter-spacing: 1px;
    width: 100%;
    box-shadow: 0 0 10px rgba(255, 51, 51, 0.4);
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: linear-gradient(135deg, #ee0000, #ff5555) !important;
    box-shadow: 0 0 15px rgba(255, 51, 51, 0.7);
}

/* 메인 화면 스타일 */
.stTitle {
    color: #ff3333 !important;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* 결과 출력 얼럿 세련되게 변경 */
.stAlert {
    background-color: #1a1c23 !important;
    border: 1px solid #2d313f !important;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# 사이드바 구성 (원본 기능 유지)
st.sidebar.title("🚨 지진 속보 모니터")
st.sidebar.markdown("---")
st.sidebar.subheader("진앙지 위치 입력")
lat = st.sidebar.number_input("위도 (Latitude)", value=37.5, format="%.4f")
lon = st.sidebar.number_input("경도 (Longitude)", value=127.0, format="%.4f")
st.sidebar.markdown("---")
analysis_button = st.sidebar.button("위험도 분석 실행")

# 메인 화면
st.title("🖥️ 지진 파동 정보 분석 시스템")
st.markdown("---")
st.write("본 시스템은 입력하신 위도와 경도 주변의 과거 지진 데이터를 분석하여 지진 위험도를 평가합니다. 공식적인 지진 예보가 아니며, 참고 자료로 활용하시기 바랍니다.")

# 버튼 클릭 시 (원본 제어 흐름 완벽 유지)
if analysis_button:

    # 주변 지진 찾기 (원본 범위 계산 로직 유지)
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

        # 위험도 출력 (방송 자막 속보 스타일 멘트 셋업)
        danger_level = risk_dict[main_cluster]
        if danger_level == '높음':
            st.error(f"⚠️ **[지진속보] 예상 위험도: 높음** — 강한 진동 유의 및 추가 여진에 대비하십시오.")
        elif danger_level == '중간':
            st.warning(f"⚠️ **[지진정보] 예상 위험도: 중간** — 주변 지역에 흔들림이 감지될 수 있습니다.")
        else:
            st.success(f"✅ **[지진정보] 예상 위험도: 낮음** — 현재 시점 기준 특이 진동 징후가 낮습니다.")

        # [UI 변경] 기존 위험 이미지 제거 완료

        # [UI 변경] 지도 생성: 비행기 스크린 및 방송 그래픽 느낌의 어두운 위성 지도(Esri) 베이스로 세팅
        esri_satellite = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS"
        
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=6, # 비행기 뷰 배율
            tiles=esri_satellite, 
            attr=attr
        )

        # -----------------------------------------------------------------
        # [UI 신규 연출] 진앙지 중심 지진파(동심원) 퍼지는 속보 그래픽 추가
        # -----------------------------------------------------------------
        wave_radii = [25, 60, 110, 170] # 중심부에서 바깥으로 퍼지는 미터 단위(km로 치환 예정)
        wave_opacities = [0.8, 0.5, 0.25, 0.1]
        wave_dashes = [None, "5, 5", "6, 10", "10, 15"]

        for r, op, dash in zip(wave_radii, wave_opacities, wave_dashes):
            folium.Circle(
                location=[lat, lon],
                radius=r * 1000, # 미터 단위 변환
                color="#FF3333",
                weight=2 if dash else 3,
                fill=True,
                fill_color="#FF3333",
                fill_opacity=op * 0.15,
                dash_array=dash
            ).add_to(m)
        # -----------------------------------------------------------------

        # 데이터 샘플링 (원본 로직 유지)
        df_sample = df_new.sample(min(500, len(df_new)), random_state=42)

        # 지도에 과거 지진 점 표시 (원본 로직 유지 + 시인성 강화)
        for i in range(len(df_sample)):

            cluster = df_sample.iloc[i]['cluster']
            scale = df_sample.iloc[i]['규모']

            folium.CircleMarker(
                location=[
                    df_sample.iloc[i]['위도'],
                    df_sample.iloc[i]['경도']
                ],
                radius=scale * 1.5, # 데이터 크기 시각화 보정
                color='white',      # 어두운 지도 위 가독성을 위한 테두리 흰색 처리
                weight=0.5,
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.75
            ).add_to(m)

        # 사용자 위치 표시 (X 혹은 레이더 포인터 모양의 마커)
        folium.Marker(
            location=[lat, lon],
            popup="진앙지 (EPICENTER)",
            icon=folium.Icon(color='red', icon='play') # 파동의 시작 지점을 뜻하는 플레이 아이콘
        ).add_to(m)

        # 스트림릿에 지도 출력 (원본 규격 유지)
        st_folium(m, use_container_width=True, height=600, returned_objects=[])

# 푸터 (컨셉에 맞추어 디자인 고도화)
st.markdown("---")
st.markdown("<p style='text-align: center; color: #525866; font-size: 0.85rem;'>EARTHQUAKE EARLY WARNING MONITORING SYSTEM | © 2026 지진 데이터 분석팀.</p>", unsafe_allow_html=True)
