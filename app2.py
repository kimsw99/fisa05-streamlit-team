import datetime
import pandas as pd
import numpy as np
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import plotly.express as px

st.set_page_config(layout="wide", page_title="전국 미디어 콘텐츠 촬영지 지도", page_icon="🎬")

# 📁 데이터 로딩
@st.cache_data
def get_filming_location_list() -> pd.DataFrame:
    return pd.read_csv('data/촬영지_데이터.csv', encoding='cp949')


# 🗺 지도 시각화 함수
def draw_map_by_search(filming_df, search_name: str, search_type: int):
    filtered_df = pd.DataFrame()

    if search_type == 1:
        filtered_df = filming_df[filming_df['주소'].str.contains(search_name.strip(), na=False)]
        lat = filtered_df['위도'].mean()
        lng = filtered_df['경도'].mean()
        m = folium.Map(location=[lat, lng], zoom_start=8, tiles='CartoDB Voyager')
    elif search_type == 2:
        filtered_df = filming_df[filming_df.제목 == search_name.strip()]
        m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB Voyager')
    else:
        return

    if filtered_df.empty:
        st.info("🔍 검색 결과가 없습니다.")
        return

    cluster = MarkerCluster().add_to(m)
    for _, row in filtered_df.iterrows():
        tooltip = f"""<b>작품명:</b> {row['제목']}<br>
                      <b>장소설명:</b> {row['장소설명']}<br>
                      <b>장소타입:</b> {row['장소타입']}"""

        folium.Marker(
            location=[row['위도'], row['경도']],
            tooltip=tooltip,
            popup=folium.Popup(
                f"""<b>장소명:</b> {row['장소명']}<br>
                    <b>주소:</b> {row['주소']}<br>
                    <b>영업시간:</b> {row['영업시간']}<br>
                    <b>전화번호:</b> {row['전화번호']}""",
                max_width=400
            )
        ).add_to(cluster)

    folium_static(m, width=1200, height=600)


# 📊 히스토그램 함수
def draw_histogram_by_search(filming_df, search_name: str, search_type: int):
    color_map = {
        'cafe': '#A45A52', 'playground': '#E89C5D',
        'restaurant': '#C4B454', 'stay': '#52606D',
        'station': '#5478A6', 'store': '#8D6C8D'
    }

    if search_type == 1:
        search = filming_df[filming_df['주소'].str.contains(search_name, na=False)]
    else:
        search = filming_df[filming_df.제목 == search_name]

    cnt_loc = search['장소타입'].value_counts().reset_index()
    cnt_loc.columns = ['장소타입', 'count']

    fig = px.pie(
        cnt_loc,
        names='장소타입',
        values='count',
        color='장소타입',
        color_discrete_map=color_map,
        title="장소 타입 분포"
    )
    fig.update_traces(textinfo='label+percent')
    return fig


# 🔍 사이드바
def sidebar_inputs(filming_df):
    location_name, program_name, confirm_btn = '', '', False
    search_type = st.sidebar.radio('검색 기준', ['주소', '프로그램명', '연예인'])

    if search_type == '주소':
        location_name = st.sidebar.text_input('지역명을 입력하세요 (예: 강남구)')
    elif search_type == '프로그램명':
        programs = sorted(set(filming_df['제목'][filming_df['미디어타입'] != 'artist']), reverse=True)
        program_name = st.sidebar.selectbox('프로그램명 선택', [''] + programs)
    elif search_type == '연예인':
        artists = sorted(set(filming_df['제목'][filming_df['미디어타입'] == 'artist']), reverse=True)
        program_name = st.sidebar.selectbox('연예인 이름 선택', [''] + artists)

    confirm_btn = st.sidebar.button('검색')
    return location_name, program_name, confirm_btn, search_type


# 🎯 데이터 필터링
def searching_data(filming_df, search_name, search_type):
    if search_type == '주소':
        return filming_df[filming_df['주소'].str.contains(search_name, na=False)]
    return filming_df[filming_df['제목'].str.contains(search_name, na=False)]


# 🏁 메인 실행
filming_df = get_filming_location_list()
location_name, program_name, confirmed, search_type = sidebar_inputs(filming_df)
screening_data = searching_data(filming_df, location_name or program_name, search_type)

if confirmed:
    st.title("🎬 촬영지 탐색 서비스")
    st.subheader(f"🔎 검색 결과: {location_name or program_name}")

    col1, col2 = st.columns([2, 1])

    with col1:
        if location_name:
            draw_map_by_search(filming_df, location_name, 1)
        elif program_name:
            draw_map_by_search(filming_df, program_name, 2)

    with col2:
        # 지도와 균형을 맞추기 위한 여백
        st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(draw_histogram_by_search(filming_df, location_name or program_name, 1 if location_name else 2))

    st.divider()

    st.subheader(f"✨ 오늘의 추천 장소 ({len(screening_data)}개 중 랜덤 선정)")

    today_seed = int(datetime.datetime.now().strftime('%Y%m%d'))
    np.random.seed(today_seed)

    today_spot = screening_data[['제목', '장소명', '영업시간', '장소설명', '전화번호', '주소']]
    if len(today_spot) >= 3:
        today_spot = today_spot.sample(n=3)

        for i, row in today_spot.iterrows():
            with st.container():
                cols = st.columns([1, 3])
                with cols[0]:
                    st.markdown("🎥 **" + row['제목'] + "**")
                with cols[1]:
                    st.markdown(f"""
                    - 📍 **장소명:** {row['장소명']}  
                    - 🕒 **영업시간:** {row['영업시간']}  
                    - 📞 **전화번호:** {row['전화번호']}  
                    - 🗺 **주소:** {row['주소']}  
                    - 💬 **설명:** {row['장소설명'][:60]}...
                    """)
            st.markdown("---")
