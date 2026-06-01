import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="슈팅스타 지진 관측 팩트",
    page_icon="💫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 불러오기 (원본 로직 완벽 유지)
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

# 위험도 사전 (티니핑 톤으로 변경)
risk_dict = {0: '피릿! 아주 위험해핑!', 1: '반짝! 안전해핑!', 2: '조심! 중간이야핑!'}

# 군집 색상 (슈팅스타팩트의 보석 컬러: 핑크, 보라, 옐로우)
colors = {0: '#FF69B4', 1: '#BA55D3', 2: '#FFD700'}

# [UI 변경] 슈팅스타팩트 마법소녀 컨셉 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

/* 전체 화면 배경: 보라색 & 핑크색 그라데이션 */
.stApp {
    background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%) !important;
}

body {
    font-family: 'Jua', sans-serif;
}

/* 사이드바 스타일: 슈팅스타팩트 핑크 */
[data-testid="stSidebar"] {
    background-color: #FFB6C1 !important;
    border-right: 5px solid #FF69B4;
}

[data-testid="stSidebar"] .stMarkdown h1, h2, h3 {
    color: #C71585 !important;
    text-shadow: 1px 1px 2px white;
}

/* 별빛 버튼 스타일 */
[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(to right, #FF69B4, #FFD700) !important;
    color: white !important;
    border-radius: 30px;
    border: 3px solid #FFF;
    font-size: 20px;
    font-weight: bold;
    height: 3em;
    width: 100%;
    box-shadow: 0 0 15px rgba(255, 105, 180, 0.6);
}

[data-testid="stSidebar"] .stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.8);
}

/* 메인 타이틀: 반짝반짝 효과 */
.stTitle {
    color: #FF1493 !important;
    font-family: 'Jua', sans-serif;
    text-align: center;
    font-size: 3rem !important;
    text-shadow: 2px 2px 5px #FFFFFF;
}

/* 결과창 스타일 */
.stAlert {
    background-color: rgba(255, 255, 255, 0.7) !important;
    border: 3px solid #FF69B4 !important;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

# 사이드바 구성 (기능 유지, 컨셉만 변경)
st.sidebar.title("💫 슈팅스타 관측")
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ 별자리 위치 입력")
lat = st.sidebar.number_input("위도 (Latitude)", value=37.5, format="%.4f")
lon = st.sidebar.number_input("경도 (Longitude)", value=127.0, format="%.4f")
st.sidebar.markdown("---")
analysis_button = st.sidebar.button("✨ 지진 에너지 캐치! ✨")

# 메인 화면
st.title("💖 슈팅스타팩트 지진 관측기 💖")
st.markdown("<h3 style='text-align: center; color: #DB7093;'>반짝반짝! 별빛의 힘으로 지진 에너지를 캐치해핑!</h3>", unsafe_allow_html=True)
st.write("---")

# 버튼 클릭 시
if analysis_button:

    # 주변 지진 찾기
    near_df = df_new[
        (df_new['위도'] >= lat - 5) &
        (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) &
        (df_new['경도'] <= lon + 5)
    ]

    if len(near_df) == 0:
        st.sidebar.warning("앗! 별빛 에너지가 부족해핑. 범위를 넓혀봐핑!")
    else:
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = cluster_ratio.idxmax()

        # 결과 출력 (티니핑 말투 반영)
        danger_level = risk_dict[main_cluster]
        if danger_level == '피릿! 아주 위험해핑!':
            st.error(f"🚨 **{danger_level}** — 슈팅스타의 힘으로 모두를 지켜야해핑!")
        elif danger_level == '조심! 중간이야핑!':
            st.warning(f"⚠️ **{danger_level}** — 살짝 흔들릴 수 있으니 조심해핑!")
        else:
            st.success(f"✨ **{danger_level}** — 오늘도 평화로운 슈팅스타 마을이야핑!")

        # 지도 생성: 팩트 안의 신비로운 마법 지도 느낌 (CartoDB Positron: 밝고 깨끗함)
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=6, 
            tiles="CartoDB positron"
        )

        # -----------------------------------------------------------------
        # [연출 변경] 슈팅스타팩트에서 퍼지는 "별빛 파동" 연출
        # -----------------------------------------------------------------
        wave_radii = [30, 70, 120, 180] 
        wave_colors = ["#FF1493", "#FF69B4", "#EE82EE", "#FFD700"]

        for r, color in zip(wave_radii, wave_colors):
            folium.Circle(
                location=[lat, lon],
                radius=r * 1000, 
                color=color,
                weight=3,
                fill=True,
                fill_color=color,
                fill_opacity=0.1,
                dash_array="10, 5" if r > 100 else None
            ).add_to(m)
        # -----------------------------------------------------------------

        # 데이터 샘플링
        df_sample = df_new.sample(min(500, len(df_new)), random_state=42)

        # 지도에 과거 지진 점 표시 (별가루 느낌)
        for i in range(len(df_sample)):
            cluster = df_sample.iloc[i]['cluster']
            scale = df_sample.iloc[i]['규모']

            folium.CircleMarker(
                location=[df_sample.iloc[i]['위도'], df_sample.iloc[i]['경도']],
                radius=scale * 2, 
                color=colors[cluster],
                weight=1,
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.6
            ).add_to(m)

        # 사용자 위치 표시 (팩트의 중심 별 모양)
        folium.Marker(
            location=[lat, lon],
            popup="슈팅스타 에너지 중심!",
            icon=folium.Icon(color='lightred', icon='star') 
        ).add_to(m)

        # 지도 출력
        st_folium(m, use_container_width=True, height=600, returned_objects=[])

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: #DB7093; font-family: Jua;'>💫 캐치! 티니핑 5기 슈팅스타팩트 시뮬레이터 💫</p>", unsafe_allow_html=True)
