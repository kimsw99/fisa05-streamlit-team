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

def draw_map_by_location(filming_df,location_name: str) -> folium_static:
    """
    입력된 지역명에 해당하는 촬영지 정보를 DataFrame으로 반환합니다.

    Args:
        location_name (str): 지역명(시/군/구)

    Returns:
        folium_static: Streamlit에서 folium 지도를 표시하기 위한 함수
    """
    filming_df = get_filming_location_list()
    filtered_df = filming_df[filming_df['주소'].str.contains(location_name, na=False)]
    
    lat = filtered_df['위도'].mean()
    lng = filtered_df['경도'].mean()

    map = folium.Map(location=[lat, lng], zoom_start=13)
    
    location = []
    
    for i in filtered_df.index:
        location.append([ filtered_df.loc[i, '위도'], filtered_df.loc[i, '경도'] ])

    MarkerCluster(location, overlay=True).add_to(map)
    return folium_static(map,width=1200, height=600)

def draw_histogram_by_location(filming_df,location_name: str):
    """
    입력된 지역명에 해당하는 촬영지의 연도별 촬영 횟수를 히스토그램으로 시각화합니다.

    Args:
        location_name (str): 지역명(시/군/구)

    Returns:
        plt: matplotlib.pyplot 객체
    """
    categories = filming_df['장소타입'].unique() # 카테고리 순서 고정
    color_map = {
        'cafe': 'tomato',
        'playground': 'mediumseagreen',
        'restaurant': 'royalblue',
        'stay': 'orchid',
        'station': 'goldenrod',
        'store': 'slategray'
    } # 카테고리 색 고정
    # search_type = input('뭐로 검색할래 (제목 or 주소)') # 검색 유형 설정
    # search_keyword = input('입력해') # 검색 내용
    search = filming_df[filming_df['주소'].str.contains(location_name, na=False)]
    categories = filming_df['장소타입'].unique()
    fig = px.histogram(search,
                    x="장소타입",
                    color="장소타입",
                    category_orders={"장소타입": categories},
                    width=1200, 
                    height=600
                    )
    
    return fig

def sidebar_inputs() -> tuple[str, bool]:
    """
    Streamlit 지역(구) 텍스트 입력, 확인 버튼을 생성하고 값을 반환합니다.

    Returns:
        tuple: (지역명(str), 확인버튼 클릭여부(bool))
    """
    location_name = st.sidebar.text_input('지역명을 입력하세요(시/군/구): ')
    confirm_btn = st.sidebar.button('확인')
    return location_name, confirm_btn

filming_df = get_filming_location_list()
location_name, confirmed = sidebar_inputs()

if confirmed:
    
    st.set_page_config(layout="wide")
    st.header(f"{location_name} 촬영지 정보")
    col1, col2 = st.columns(2)
    with col1:
        draw_map_by_location(filming_df,location_name)

    with col2:
        st.plotly_chart(draw_histogram_by_location(filming_df,location_name))
    