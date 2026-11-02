
import folium
from streamlit_folium import st_folium

# ----------------------------------
# 1. 페이지 기본 설정
# ----------------------------------
st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide",
)

# ----------------------------------
# 2. 관광지 데이터
# 좌표는 지도 표시용 대표 좌표입니다.
# 공식 실시간 인기 순위는 아닙니다.
# ----------------------------------
SPOTS = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": (
            "조선 왕조의 대표 궁궐로, 한국의 전통 건축과 "
            "수문장 교대 의식을 경험할 수 있어요."
        ),
        "tip": "한복을 입고 방문하면 특별한 사진을 남기기 좋아요.",
    },
    {
        "rank": 2,
        "name": "북촌 한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·산책",
        "description": (
            "전통 한옥이 모여 있는 동네로, 골목길과 한옥 "
            "지붕 너머로 서울의 풍경을 볼 수 있어요."
        ),
        "tip": "실제 주민들이 생활하는 곳이므로 조용히 둘러봐 주세요.",
    },
    {
        "rank": 3,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": (
            "화장품 매장과 쇼핑 거리, 다양한 길거리 음식으로 "
            "유명한 번화가예요."
        ),
        "tip": "저녁에는 길거리 음식 매대가 활기를 띠는 경우가 많아요.",
    },
    {
        "rank": 4,
        "name": "홍대거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": (
            "개성 있는 카페와 상점, 거리 공연, 음악 문화가 "
            "어우러진 활기찬 지역이에요."
        ),
        "tip": "주말에는 사람이 많을 수 있으니 이동 시간을 여유 있게 잡아 보세요.",
    },
    {
        "rank": 5,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": (
            "남산에 자리한 서울의 대표 랜드마크로, 전망대에서 "
            "도심 풍경을 감상할 수 있어요."
        ),
        "tip": "날씨가 맑은 날 방문하면 전망을 즐기기 더 좋아요.",
    },
    {
        "rank": 6,
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·디자인",
        "description": (
            "독특한 곡선형 건축물과 전시, 디자인 행사가 "
            "열리는 현대적인 문화 공간이에요."
        ),
        "tip": "방문 전 공식 홈페이지에서 전시와 행사 일정을 확인해 보세요.",
    },
    {
        "rank": 7,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5740,
        "lon": 126.9857,
        "category": "전통·공예",
        "description": (
            "전통 공예품, 갤러리, 찻집과 한국적인 기념품을 "
            "만날 수 있는 거리예요."
        ),
        "tip": "골목 안쪽의 작은 공방과 찻집도 둘러보세요.",
    },
    {
        "rank": 8,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5692,
        "lon": 126.9788,
        "category": "산책·자연",
        "description": (
            "서울 도심을 가로지르는 하천 산책로로, "
            "도심 속에서 잠시 쉬어 가기 좋아요."
        ),
        "tip": "비가 많이 오거나 통제 안내가 있을 때는 현장 안내를 따라 주세요.",
    },
    {
        "rank": 9,
        "name": "롯데월드타워·서울스카이",
        "english": "Lotte World Tower & Seoul Sky",
        "lat": 37.5125,
        "lon": 127.1025,
        "category": "전망·쇼핑",
        "description": (
            "높은 전망대 서울스카이와 쇼핑·식사를 함께 "
            "즐길 수 있는 대형 복합 공간이에요."
        ),
        "tip": "전망대 입장권과 운영시간은 방문 전에 확인하는 것이 좋아요.",
    },
    {
        "rank": 10,
        "name": "국립중앙박물관",
        "english": "National Museum of Korea",
        "lat": 37.5239,
        "lon": 126.9804,
        "category": "역사·박물관",
        "description": (
            "한국의 역사와 예술을 폭넓게 살펴볼 수 있는 "
            "대표 박물관이에요."
        ),
        "tip": "관람 시간이 넉넉하지 않다면 관심 있는 전시부터 둘러보세요.",
    },
]

# ----------------------------------
# 3. 앱 제목 및 안내
# ----------------------------------
st.title("🗺️ 서울 인기 관광지 TOP 10")

st.write(
    "서울 여행을 계획하는 분들을 위한 대표 관광지 지도예요. "
    "지도에서 번호 마커를 누르거나 아래 목록을 확인해 보세요!"
)

st.caption(
    "※ 외국인 여행자에게 소개하기 좋은 대표 명소를 선정한 "
    "추천 목록이며, 공식 실시간 인기 순위는 아닙니다."
)

# ----------------------------------
# 4. 사이드바 검색 및 필터
# ----------------------------------
with st.sidebar:
    st.header("🔎 관광지 찾기")

    categories = ["전체"] + sorted(
        {spot["category"] for spot in SPOTS}
    )

    selected_category = st.selectbox(
        "분야 선택",
        categories,
    )

    search_text = st.text_input(
        "관광지 이름 검색",
        placeholder="예: 명동, 궁궐, 박물관",
    )

    st.markdown("---")

    st.caption(
        "지도는 OpenStreetMap을 사용합니다. "
        "지도를 보려면 인터넷 연결이 필요해요."
    )

# ----------------------------------
# 5. 검색 조건에 맞는 관광지 선택
# ----------------------------------
keyword = search_text.strip().lower()

filtered_spots = [
    spot
    for spot in SPOTS
    if (
        selected_category == "전체"
        or spot["category"] == selected_category
    )
    and (
        not keyword
        or keyword in spot["name"].lower()
        or keyword in spot["english"].lower()
        or keyword in spot["category"].lower()
    )
]

# ----------------------------------
# 6. 지도와 오른쪽 안내 영역
# ----------------------------------
map_col, info_col = st.columns(
    [2, 1],
    gap="large",
)

with map_col:
    st.subheader("📍 관광지 위치")

    # 서울 중심 좌표로 지도 생성
    seoul_map = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # 검색 결과에 해당하는 관광지만 지도에 표시
    for spot in filtered_spots:

        popup_html = f"""
        <div style="width:220px">
            <strong>
                {spot['rank']}. {spot['name']}
            </strong>
            <br>
            <em>{spot['english']}</em>
            <br>
            <small>{spot['category']}</small>
            <br><br>
            {spot['description']}
        </div>
        """

        # 번호가 표시되는 원형 마커
        folium.Marker(
            location=[
                spot["lat"],
                spot["lon"],
            ],
            tooltip=f"{spot['rank']}. {spot['name']}",
            popup=folium.Popup(
                popup_html,
                max_width=280,
            ),
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background:#1769aa;
                    color:white;
                    border:2px solid white;
                    border-radius:50%;
                    width:30px;
                    height:30px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-weight:bold;
                    font-size:13px;
                    box-shadow:0 1px 5px rgba(0,0,0,.45);
                ">
                    {spot['rank']}
                </div>
                """,
                icon_size=(30, 30),
                icon_anchor=(15, 15),
            ),
        ).add_to(seoul_map)

    # 표시된 관광지들이 화면에 들어오도록 지도 범위 조정
    if filtered_spots:
        bounds = [
            [spot["lat"], spot["lon"]]
            for spot in filtered_spots
        ]

        seoul_map.fit_bounds(
            bounds,
            padding=(25, 25),
        )
    else:
        st.info(
            "검색 조건에 맞는 관광지가 없어요. "
            "검색어나 분야를 바꿔 보세요."
        )

    # Streamlit 화면에 지도 표시
    st_folium(
        seoul_map,
        height=580,
        use_container_width=True,
        returned_objects=[],
        key="seoul_tourism_map",
    )

with info_col:
    st.subheader("✨ 여행 팁")

    st.markdown(
        """
        - **전통 문화:** 경복궁, 북촌 한옥마을, 인사동
        - **쇼핑·거리 문화:** 명동, 홍대거리
        - **전망·건축:** N서울타워, DDP, 롯데월드타워
        - **휴식·배움:** 청계천, 국립중앙박물관
        """
    )

    st.info(
        "이동 전에는 각 장소의 공식 안내에서 운영시간, "
        "휴관일, 입장 정보를 확인하세요."
    )

# ----------------------------------
# 7. 지도 아래 관광지 소개
# ----------------------------------
st.divider()

st.header("📚 관광지 소개")

st.write(
    "각 장소의 특징과 간단한 방문 팁을 확인해 보세요."
)

if not filtered_spots:
    st.warning("표시할 관광지가 없습니다.")

else:
    # 두 개의 열에 관광지 카드 배치
    card_cols = st.columns(2, gap="medium")

    for index, spot in enumerate(filtered_spots):

        with card_cols[index % 2]:

            with st.container(border=True):

                st.markdown(
                    f"### {spot['rank']}. {spot['name']}"
                )

                st.caption(
                    f"{spot['english']} · {spot['category']}"
                )

                st.write(spot["description"])

                st.markdown(
                    f"💡 **방문 팁:** {spot['tip']}"
                )

                google_maps_url = (
                    "https://www.google.com/maps/search/"
                    f"?api=1&query={spot['lat']},{spot['lon']}"
                )

                st.link_button(
                    "Google 지도에서 위치 보기",
                    google_maps_url,
                    use_container_width=True,
                )

# ----------------------------------
# 8. 하단 안내
# ----------------------------------
st.divider()

st.caption(
    "관광지 위치는 지도 표시용 대표 좌표입니다. "
    "실제 출입구나 방문 동선과는 차이가 있을 수 있어요."
)
