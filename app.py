# 표준 라이브러리
import datetime
from io import BytesIO

# 서드파티 라이브러리
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
import matplotlib 
# import koreanize_matplotlib

@st.cache_data
def get_filming_location_list() -> pd.DataFrame:
    """
    전국 미디어콘텐츠 촬영지 정보를 DataFrame으로 반환합니다.

    Returns:
        pd.DataFrame: 모든 칼럼을 가진 DataFrame
    """
    filming_df = pd.read_csv('data/촬영지_데이터.csv',encoding='cp949')
    return filming_df

def draw_map_by_search(filming_df, search_name: str, search_type: int):
    filtered_df = pd.DataFrame()  # 기본값 설정

    if search_type == 1:
        filtered_df = filming_df[filming_df['주소'].str.contains(search_name.strip(), na=False)]
        lat = filtered_df['위도'].mean()
        lng = filtered_df['경도'].mean()
        m = folium.Map(location=[lat, lng], zoom_start=8, tiles='CartoDB Voyager')

    elif search_type == 2:
        if search_name:  # None이나 빈 문자열 체크
            filtered_df = filming_df[filming_df.제목 == search_name.strip()]
            m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB Voyager')
        else:
            st.warning("검색어가 입력되지 않았습니다.")
            return

    else:
        st.error("유효하지 않은 검색 타입입니다.")
        return

    if filtered_df.empty:
        st.info("검색 결과가 없습니다.")
        return

    # 마커 추가
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

    return folium_static(m, width=1200, height=600)


def draw_histogram_by_search(filming_df,search_name: str, search_type: int):
    """
    입력된 지역명에 해당하는 촬영지의 연도별 촬영 횟수를 히스토그램으로 시각화합니다.

    Args:
        location_name (str): 지역명(시/군/구)

    Returns:
        plt: matplotlib.pyplot 객체
    """

    categories = filming_df['장소타입'].unique() # 카테고리 순서 고정
    color_map = {
    'cafe':       '#A45A52',
    'playground': '#E89C5D', 
    'restaurant': '#C4B454', 
    'stay':       '#52606D', 
    'station':    '#5478A6', 
    'store':      '#8D6C8D', 
    }

    # 카테고리 색 고정
    # search_type = input('뭐로 검색할래 (제목 or 주소)') # 검색 유형 설정
    # search_keyword = input('입력해') # 검색 내용
    if search_type == 1:
        search = filming_df[filming_df['주소'].str.contains(search_name, na=False)]
    else:   
        search = filming_df[filming_df.제목 == search_name]
    
    categories = filming_df['장소타입'].unique()

    # 파이플롯 생성을 위해 value_counts
    cnt_loc = search['장소타입'].value_counts()

    # 시리즈를 데이터 프레임으로 변환
    cnt_loc = cnt_loc.reset_index()
    cnt_loc.columns = ['장소타입', 'count']

    fig = px.pie(
            cnt_loc,
            names = '장소타입',
            values = 'count',
            color = '장소타입',
            color_discrete_map = color_map,
            title = location_name
            )
    fig.update_traces(textinfo = 'label')
    
    return fig

def sidebar_inputs(filming_df) -> tuple[str, str, bool]:
    location_name, program_name = '', ''
    confirm_btn = False

    search_type = st.sidebar.radio('검색', ['주소', '프로그램명', '연예인'])

    if search_type == '주소':
        location_name = st.sidebar.text_input('지역명을 입력하세요(시/군/구): ')
    elif search_type == '프로그램명':
        programs = sorted(set(filming_df['제목'][filming_df['미디어타입'] != 'artist']))
        program_name = st.sidebar.selectbox('프로그램명을 선택하세요: ', [''] + programs)
        st.sidebar.write(program_name)
    elif search_type == '연예인':
        artists = sorted(set(filming_df['제목'][filming_df['미디어타입'] == 'artist']))
        program_name = st.sidebar.selectbox('연예인을 선택하세요: ', [''] + artists)
        
    confirm_btn = st.sidebar.button('확인')

    return location_name, program_name, confirm_btn


# main 실행부
filming_df = get_filming_location_list()
location_name, program_name, confirmed = sidebar_inputs(filming_df)

if confirmed:
    st.set_page_config(layout="wide")
    st.header(f"{location_name or program_name} 촬영지 정보")
    col1, col2 = st.columns(2)

    if location_name:
        with col1:
            draw_map_by_search(filming_df, location_name, 1)
        with col2:
            st.plotly_chart(draw_histogram_by_search(filming_df, location_name, 1))
    elif program_name:
        with col1:
            draw_map_by_search(filming_df, program_name, 2)
        with col2:
            st.plotly_chart(draw_histogram_by_search(filming_df, program_name, 2))
    