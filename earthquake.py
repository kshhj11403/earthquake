import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

# 페이지 설정 (귀여운 별빛 컨셉)
st.set_page_config(
    page_title="슈팅스타팩트 - 지진 에너지 캐치!",
    page_icon="💫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 불러오기 (기존 데이터 로직 완벽 유지)
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

# 위험도 사전 (티니핑 5기 슈팅스타 컨셉 멘트)
risk_dict = {
    0: '🚨 피릿! 엄청 강력한 에너지가 뿜어져 나오고 있어핑! 위험해핑!', 
    1: '💖 반짝! 대지가 아주 평온하고 튼튼해핑! 안전해핑!', 
    2: '💛 조심! 별빛 에너지가 살짝 흔들리고 있어핑! 중간이야핑!'
}

# 슈팅스타 마법 보석 색상셋 (핑크, 퍼플, 골드 옐로우)
colors = {0: '#FF1493', 1: '#9400D3', 2: '#FFD700'}

# [UI 고도화] 슈팅스타팩트 완구 외형 및 동그란 액정 스크린 커스텀 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

/* 슈팅스타팩트 내부 마법 공간 느낌의 파스텔 그라데이션 배경 */
.stApp {
    background: linear-gradient(135deg, #FFE4E1 0%, #E6E6FA 50%, #E0FFFF 100%) !important;
}

body, p, span, label {
    font-family: 'Jua', sans-serif !important;
    color: #4A0E4E !important;
}

/* 사이드바: 완구 본체의 핑크빛 플라스틱 질감 연출 */
[data-testid="stSidebar"] {
    background-color: #FFB6C1 !important;
    border-right: 5px solid #FF69B4;
    box-shadow: 5px 0px 15px rgba(255, 105, 180, 0.3);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #FF1493 !important;
    text-shadow: 2px 2px 0px #FFFFFF;
}

/* 마법 발동 버튼 (슈팅스타팩트 중앙 보석 버튼 스타일) */
[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(135deg, #FF69B4, #FFD700) !important;
    color: white !important;
    border-radius: 25px !important;
    border: 3px solid #FFFFFF !important;
    font-size: 1.25rem !important;
    font-weight: bold !important;
    padding: 12px 20px !important;
    width: 100%;
    box-shadow: 0 0 15px rgba(255, 105, 180, 0.6);
    transition: all 0.3s ease;
}
[data-testid="stSidebar"] .stButton>button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.9);
}

/* 메인 화면 타이틀 */
.stTitle {
    color: #FF1493 !important;
    text-shadow: 3px 3px 0px #FFFFFF, 0px 0px 10px rgba(255, 20, 147, 0.3);
    text-align: center;
    font-size: 2.8rem !important;
    margin-bottom: 20px;
}

/* 티니핑 알림창 커스텀 */
.stAlert {
    background-color: rgba(255, 255, 255, 0.85) !important;
    border: 3px dashed #FF69B4 !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* -----------------------------------------------------------------
   [신규 기능] 슈팅스타팩트 본체 모양의 동그란 팩트 스크린 레이아웃
   ----------------------------------------------------------------- */
.compact-frame {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px 0;
}

.compact-screen {
    width: 540px;
    height: 540px;
    border-radius: 50% !important; /* 지도를 동그랗게 깎아냄 */
    border: 18px solid #FF69B4;   /* 완구 특유의 마법 핑크 프레임 */
    box-shadow: 0 0 0 8px #FFD700, /* 금빛 보석 라인 추가 */
                0 0 30px rgba(255, 20, 147, 0.6), 
                inset 0 0 20px rgba(0, 0, 0, 0.2);
    overflow: hidden;              /* 경계선 밖으로 나가는 지도를 잘라내기 */
    background-color: #ffffff;
}

/* 스트림릿 folium 내부 컨테이너 강제 둥글게 깎기 고정 */
.compact-screen iframe {
    border-radius: 50% !important;
    width: 100% !important;
    height: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# 사이드바 구성 (입력 조작계)
st.sidebar.title("💫 슈팅스타 팩트")
st.sidebar.markdown("---")
st.sidebar.subheader("🔮 관측할 별자리 좌표")
lat = st.sidebar.number_input("위도 (Latitude)", value=37.5, format="%.4f")
lon = st.sidebar.number_input("경도 (Longitude)", value=127.0, format="%.4f")
st.sidebar.markdown("---")
analysis_button = st.sidebar.button("✨ 스타 파워 에너지를 캐치! ✨")

# 메인 화면 (슈팅스타팩트 스크린 레이아웃)
st.title("💖 슈팅스타팩트 마법 지도 시스템 💖")
st.markdown("<p style='text-align: center; font-size: 1.25rem; color: #BA55D3;'>반짝반짝 슈팅스타! 대지의 기운을 모아 지구의 평화를 지켜줘핑!</p>", unsafe_allow_html=True)
st.markdown("---")

# 마법 버튼을 누르면 탐색 시작
if analysis_button:

    # 주변 지진 탐색 범위 지정 (기존 데이터 처리 기능 100% 동일)
    near_df = df_new[
        (df_new['위도'] >= lat - 5) &
        (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) &
        (df_new['경도'] <= lon + 5)
    ]

    if len(near_df) == 0:
        st.sidebar.warning("앗! 이 근처에는 별빛 에너지가 닿지 않아핑. 다른 곳을 찾아봐핑!")
    else:
        # 가장 우세한 위험도 클러스터 연산
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = cluster_ratio.idxmax()
        danger_level = risk_dict[main_cluster]

        # 티니핑 스크린 경보 알림 연출
        if main_cluster == 0:
            st.error(f"**{danger_level}**")
        elif main_cluster == 2:
            st.warning(f"**{danger_level}**")
        else:
            st.success(f"**{danger_level}**")

        # 팩트 액정 안에 띄워질 화사하고 예쁜 매직 지도 레이어 (CartoDB Positron)
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=6, 
            tiles="CartoDB positron"
        )

        # -----------------------------------------------------------------
        # [슈팅스타 전용 연출] 팩트 중심부에서 뿜어지는 반짝반짝 별빛 파동(동심원)
        # -----------------------------------------------------------------
        wave_radii = [30, 75, 130, 200] 
        wave_colors = ["#FF1493", "#FF69B4", "#BA55D3", "#FFD700"]

        for r, color in zip(wave_radii, wave_colors):
            folium.Circle(
                location=[lat, lon],
                radius=r * 1000, 
                color=color,
                weight=3,
                fill=True,
                fill_color=color,
                fill_opacity=0.08,
                dash_array="8, 6" if r > 100 else None
            ).add_to(m)
        # -----------------------------------------------------------------

        # 과거 지진 이력 샘플링 가시화
        df_sample = df_new.sample(min(500, len(df_new)), random_state=42)

        # 지도 위에 별가루 도트(과거 지진 데이터) 뿌리기
        for i in range(len(df_sample)):
            cluster = df_sample.iloc[i]['cluster']
            scale = df_sample.iloc[i]['규모']

            folium.CircleMarker(
                location=[
                    df_sample.iloc[i]['위도'],
                    df_sample.iloc[i]['경도']
                ],
                radius=scale * 1.8, 
                color=colors[cluster],
                weight=1,
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.6
            ).add_to(m)

        # 현재 관측 중인 요석/진앙 센터 (반짝이는 마법 별빛 마커)
        folium.Marker(
            location=[lat, lon],
            popup="슈팅스타 게이트",
            icon=folium.Icon(color='purple', icon='star') 
        ).add_to(m)

        # -----------------------------------------------------------------
        # [변경 포인트] 지도를 슈팅스타팩트의 동그란 기기 화면 컴포넌트 내부에 삽입
        # -----------------------------------------------------------------
        st.markdown('<div class="compact-frame">', unsafe_allow_html=True)
        st.markdown('<div class="compact-screen">', unsafe_allow_html=True)
        
        # 둥근 팩트 크기에 알맞게 지도 크기를 정방향(500x500)으로 맞춰 출력합니다.
        st_folium(m, width=500, height=500, returned_objects=[])
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # -----------------------------------------------------------------

# 화면 하단 푸터 레이블
st.markdown("---")
st.markdown("<p style='text-align: center; color: #9370DB; font-size: 0.9rem;'>💫 캐치! 티니핑 5기 슈팅스타팩트 완구 가상 연동 인터페이스 | © 2026 스타티니핑 본부</p>", unsafe_allow_html=True)
