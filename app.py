# 표준 라이브러리
import datetime
from io import BytesIO

# 서드파티 라이브러리
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.express as px
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
import matplotlib 
from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
    
@st.cache_data
def get_filming_location_list() -> pd.DataFrame:
    """
    전국 미디어콘텐츠 촬영지 정보를 DataFrame으로 반환합니다.

    Returns:
        pd.DataFrame: 모든 칼럼을 가진 DataFrame
    """
    filming_df = pd.read_csv('data/filtered_media_loc.csv')
    return filming_df

def draw_map_by_search(filming_df, search_name: str, search_type: int):
    filtered_df = pd.DataFrame()  # 기본값 설정

    if search_type == 1:
        filtered_df = filming_df[filming_df['상세주소'].str.contains(search_name.strip(), na=False)]
        lat = filtered_df['위도'].mean()
        lng = filtered_df['경도'].mean()
        # lat/lng NaN 여부 확인
        if pd.isna(lat) or pd.isna(lng):
            st.warning("주소명을 다시 확인해 주세요. ex) 춘천시 강남동")
            return
        m = folium.Map(location=[lat, lng], zoom_start=12, tiles='CartoDB Voyager')
        #m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB Voyager')
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
        search = filming_df[filming_df['상세주소'].str.contains(search_name, na=False)]
    else:   
        search = filming_df[filming_df['제목'] == search_name]
    
    categories = filming_df['장소타입'].unique()

    # 파이플롯 생성을 위해 value_counts
    cnt_loc = search['장소타입'].value_counts()

    # 시리즈를 데이터 프레임으로 변환
    cnt_loc = cnt_loc.reset_index()
    cnt_loc.columns = ['장소타입', 'count']

    st.subheader(f"장소 타입 분포")
    
    fig = px.pie(
            cnt_loc,
            names = '장소타입',
            values = 'count',
            color = '장소타입',
            color_discrete_map = color_map,
            )
    fig.update_traces(textinfo = 'label')
    
    return fig

def sidebar_inputs(filming_df) -> tuple[str, str, bool]:
    location_name, program_name = '', ''
    confirm_btn = False

    search_type = st.sidebar.radio('검색', ['주소', '프로그램명', '연예인'])

    if search_type == '주소':
        location_name = st.sidebar.text_input('지역명을 입력하세요(시/군/구): ',placeholder='ex) 서울특별시 강남구')
    elif search_type == '프로그램명':
        programs = sorted(set(filming_df['제목'][filming_df['미디어타입'] != 'artist']),reverse=True)
        program_name = st.sidebar.selectbox('프로그램명을 선택하세요: ', [''] + programs)
    elif search_type == '연예인':
        artists = sorted(set(filming_df['제목'][filming_df['미디어타입'] == 'artist']),reverse=True)
        program_name = st.sidebar.selectbox('연예인을 선택하세요: ', [''] + artists)
        
    confirm_btn = st.sidebar.button('확인')

    return location_name, program_name, confirm_btn, search_type

# 장소추천 데이터 탐색 함수
def searching_data(filming_df,search_name: tuple, search_type: str):
    if search_type == '주소':
        search = filming_df[filming_df['상세주소'].str.contains(search_name[0], na=False)]
    else:   
        search = filming_df[filming_df['제목'] ==search_name[1]]
    
    return search

# 지역별, 카테고리별 갯수 파악 및 막대 그래프 그리기
def many_area(filming_df:pd.DataFrame, search_type:str =''):

    # 갯수를 셀 빈 딕셔너리 생성
    cnt_array = {}
    # 지역명이 들은 리스트
    region_names = ['서울','인천','대전','광주','울산','부산','경기','충청북도','충청남도','경상북도','경상남도','전라북도','전라남도']
    
    # 지역명을 순회하며 각 명소들을 count
    for region_name in region_names:
        if search_type == 'ALL':
            cnt_array[region_name] = filming_df['주소'][filming_df['주소'].str.contains(region_name)].count()
        else:
            cnt_array[region_name] = filming_df['주소'][(filming_df['주소'].str.contains(region_name)) & (filming_df['장소타입'] == search_type)].count()

    # 딕셔너리를 value순으로 내림차순 정렬
    cnt_array = dict(sorted(cnt_array.items(), key=lambda x: x[1], reverse=True))
    # 딕셔너리를 데이터프레임으로 전환
    df_cnt = pd.DataFrame(list(cnt_array.items()), columns=['지역명', '명소 갯수'])

    # 막대 그래프 그리기
    fig = px.bar(df_cnt, x='지역명', y='명소 갯수', text_auto='.2s')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    if search_type != 'ALL':
        fig.update_yaxes(title_text=f'{search_type}의 갯수')
    elif search_type == 'ALL':
        fig.update_yaxes(title_text=f'모든 명소의 수')
    return fig

# main 실행부 

filming_df = get_filming_location_list()
location_name, program_name, confirmed, search_type = sidebar_inputs(filming_df)
screening_data = searching_data(filming_df, (location_name, program_name), search_type)
    
st.title("🎬 우리동네 명장면")
tab1 , tab2, tab3 = st.tabs(['📍 촬영지 탐색', '📊 통계', '👣 누적 지도'])
with tab1:
    if confirmed:
        
        st.set_page_config(layout="wide")
        st.header(f"{location_name or program_name} 촬영지 정보")
        col1, col2 = st.columns([1.25,1])

        if location_name:
            with col1:
                draw_map_by_search(filming_df, location_name, 1)
            with col2:
                st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)  # 높이 조절
                st.plotly_chart(draw_histogram_by_search(filming_df, location_name, 1))
        elif program_name:
            with st.container():
                with col1:
                    draw_map_by_search(filming_df, program_name, 2)
                with col2:
                    #st.plotly_chart(draw_histogram_by_search(filming_df, program_name, 2))
                    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)  # 높이 조절
                    st.plotly_chart(draw_histogram_by_search(filming_df, program_name, 2))
        
        #구분선 추가
        st.divider()
                
        with st.container():
            st.subheader(f"✨ 오늘의 추천 장소 ({len(screening_data)}개 중 랜덤 선정)")
    
            # 오늘 날짜를 시드값으로 설정
            today_seed = int(datetime.datetime.now().strftime('%Y%m%d'))
            np.random.seed(today_seed)

            # 현재 추출된 데이터를 기반으로 랜덤으로 3개 추출하여 표시
            today_spot = screening_data[['제목', '장소명', '영업시간', '장소설명', '전화번호', '주소']]
            
            if len(today_spot) > 0:
                sample_size = min(5, len(today_spot))
                today_spot = today_spot.sample(n=sample_size)

                for i, row in today_spot.iterrows():
                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            st.markdown("**" + row['제목'] + "**")
                        with cols[1]:
                            st.markdown(f"""
                            - 📍 **장소명:** {row['장소명']}  
                            - 🕒 **영업시간:** {row['영업시간']}  
                            - 📞 **전화번호:** {row['전화번호']}  
                            - 🗺 **주소:** {row['주소']}  
                            - 💬 **설명:** {row['장소설명'][:60]}...
                            """)
                    st.markdown("---")
with tab2:
    st.set_page_config(layout="wide")

    st.subheader("📊 장소타입 × 지역별 명소 갯수")
    # 목록 리스트를 생성하고, 그래프 그리기
    select_list = ['ALL','역','식당','상점','카페','촬영지','숙박 시설']
    select_ = st.selectbox('선택', select_list)
    st.plotly_chart(many_area(filming_df, select_))
    
    st.subheader("📊 미디어타입 × 장소타입 히트맵 (촬영지 제외)")

    # 촬영지를 제외한 데이터만 사용
    filtered_df = filming_df

    pivot_1 = filtered_df.groupby(['미디어타입', '장소타입']).size().reset_index(name='count')

    fig1 = px.density_heatmap(
        pivot_1, 
        x="장소타입", 
        y="미디어타입", 
        z="count",
        color_continuous_scale="YlGnBu",
        text_auto=True,
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🏠 장소별 방문 횟수 상위 TOP10")
    top_places = filming_df['장소명'].value_counts().head(10).reset_index()
    top_places.columns = ['장소명', '방문횟수']

    fig5 = px.bar(
        top_places,
        x="방문횟수",
        y="장소명",
        orientation="h",
        color="방문횟수",
        color_continuous_scale="viridis",
        height=400
    )
    st.plotly_chart(fig5, use_container_width=True)
with tab3:
    st.set_page_config(layout="wide")

    st.subheader("👣 전국 촬영지 누적지도")

    # :흰색_확인_표시: 클러스터링
    cluster_df = filming_df[['미디어타입', '위도', '경도']].dropna()
    cluster_df = cluster_df[(cluster_df['위도'] != 0) & (cluster_df['경도'] != 0)]
    cluster_df['미디어타입별_cluster'] = -1
    centroid_dict = {}
    for media in cluster_df['미디어타입'].unique():
        temp_df = cluster_df[cluster_df['미디어타입'] == media]
        coords = temp_df[['위도', '경도']].values
        if len(coords) > 0:
            kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
            kmeans.fit(coords)
            cluster_df.loc[temp_df.index, '미디어타입별_cluster'] = 0
            centroid_dict[media] = kmeans.cluster_centers_[0]
    # :흰색_확인_표시: 시각화
    #fig, ax = plt.subplots(figsize=(8,6)) 8,10이 지피티가 남한비율 최적화라함
    fig, ax = plt.subplots(figsize=(8, 10), dpi=100)  # 6*100=600px, 4*100=400px 크기
    # fig.set_dpi(100)  # 6*100=600px, 4*100=400px 크기
    for media in cluster_df['미디어타입'].unique():
        temp = cluster_df[cluster_df['미디어타입'] == media]
        ax.scatter(temp['경도'], temp['위도'], label=media, alpha=0.5)
    for i, (media, (lat, lon)) in enumerate(centroid_dict.items()):
        plt.scatter(lon, lat, c='black', marker='X', s=50)
        plt.text(lon + 0.08, lat + 0.01, f"{media}", fontsize=9, color='black', rotation=45)

    ax.legend()
    ax.set_title("전국 촬영지 누적지도")
    ax.set_xlabel("경도")
    ax.set_ylabel("위도")
    st.pyplot(fig)
    