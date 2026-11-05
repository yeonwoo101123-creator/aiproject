
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path
import math

# ---------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------

st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="🏙️",
    layout="wide"
)

# ---------------------------------------
# 2. 제목
# ---------------------------------------

st.title("🏙️ 서울시 연령별 인구 분석")
st.markdown(
    "행정구역, 성별, 연도를 선택하여 "
    "연령대별 인구수를 확인해 보세요! 😊"
)

st.divider()

# ---------------------------------------
# 3. CSV 파일 경로 찾기
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CSV_PATHS = [
    BASE_DIR / "population.csv",
    BASE_DIR.parent / "population.csv"
]

CSV_PATH = next(
    (path for path in CSV_PATHS if path.exists()),
    None
)

if CSV_PATH is None:
    st.error(
        "population.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더 또는 상위 폴더에 "
        "CSV 파일이 있는지 확인해 주세요."
    )
    st.stop()


# ---------------------------------------
# 4. CSV 파일 읽기
# 한글 인코딩 오류 방지
# ---------------------------------------

@st.cache_data
def load_data(file_path):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding,
                dtype=str
            )
            return data

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "CSV 파일의 한글 인코딩을 확인할 수 없습니다."
    )


try:
    df = load_data(str(CSV_PATH))

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# ---------------------------------------
# 5. 행정구역 이름 정리
# ---------------------------------------

df["행정구역"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)

# ---------------------------------------
# 6. 연도와 성별 선택
# ---------------------------------------

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

# 행정구역 목록
regions = df["행정구역"].dropna().unique().tolist()

with col1:
    selected_region = st.selectbox(
        "📍 행정구역",
        regions
    )

with col2:
    selected_gender = st.selectbox(
        "👤 성별",
        ["전체", "남성", "여성"]
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도",
        ["2020", "2021", "2022",
         "2023", "2024", "2025"],
        index=5
    )

st.divider()

# ---------------------------------------
# 7. 성별에 따른 데이터 열 선택
# ---------------------------------------

gender_mapping = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}

gender_key = gender_mapping[selected_gender]

# ---------------------------------------
# 8. 연령별 데이터 추출
# ---------------------------------------

age_data = {}

for column in df.columns:

    pattern = (
        rf"^{selected_year}년_"
        rf"{gender_key}거주자_(.+)$"
    )

    match = re.match(pattern, column)

    if match:

        age_group = match.group(1)

        # 총인구, 연령구간인구수는 제외
        if age_group in [
            "총인구수",
            "연령구간인구수"
        ]:
            continue

        age_data[age_group] = column


# 연령 순서 정렬
def age_sort_key(age):

    if age == "100세 이상":
        return 1000

    numbers = re.findall(r"\d+", age)

    if numbers:
        return int(numbers[0])

    return 999


age_groups = sorted(
    age_data.keys(),
    key=age_sort_key
)

if not age_groups:
    st.error(
        "선택한 연도와 성별에 해당하는 "
        "연령별 데이터가 없습니다."
    )
    st.stop()


# ---------------------------------------
# 9. 선택한 행정구역 데이터 추출
# ---------------------------------------

selected_data = df[
    df["행정구역"] == selected_region
]

if selected_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]

# ---------------------------------------
# 10. 인구수 숫자 변환
# ---------------------------------------

population = []

for age in age_groups:

    column = age_data[age]

    value = str(selected_data[column])

    value = value.replace(",", "").strip()

    try:
        population.append(float(value))
    except (ValueError, TypeError):
        population.append(0)


# ---------------------------------------
# 11. 데이터프레임 생성
# ---------------------------------------

chart_df = pd.DataFrame({
    "나이": age_groups,
    "인구수": population
})

chart_df["인구수"] = chart_df["인구수"].astype(int)

total_population = chart_df["인구수"].sum()

# ---------------------------------------
# 12. 주요 정보 표시
# ---------------------------------------

st.subheader("📊 분석 결과")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "선택한 행정구역",
        selected_region
    )

with m2:
    st.metric(
        "선택한 연도",
        f"{selected_year}년"
    )

with m3:
    st.metric(
        "연령별 인구 합계",
        f"{total_population:,}명"
    )

st.divider()

# ---------------------------------------
# 13. 파스텔톤 하늘색 꺾은선 그래프
# ---------------------------------------

st.subheader("👶 연령대별 인구수")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["나이"],
        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color="#A7D8F0",
            width=4
        ),

        marker=dict(
            color="#8CCBE8",
            size=9,
            line=dict(
                color="#FFFFFF",
                width=1.5
            )
        ),

        hovertemplate=(
            "나이: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

# ---------------------------------------
# 14. 그래프 디자인
# ---------------------------------------

max_population = max(population) if population else 0

# 세로축 범위 계산
y_max = max(
    100,
    math.ceil(max_population / 100) * 100
)

fig.update_layout(

    title=dict(
        text=(
            f"{selected_region} "
            f"{selected_year}년 "
            f"{selected_gender} 연령별 인구"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=22)
    ),

    height=650,

    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",

    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#444444"
    ),

    hovermode="x unified",

    showlegend=False,

    margin=dict(
        l=80,
        r=30,
        t=90,
        b=80
    )
)

# ---------------------------------------
# 15. 가로축 설정
# 10살 단위 구분선
# ---------------------------------------

fig.update_xaxes(

    title_text="나이",

    type="category",

    categoryorder="array",
    categoryarray=age_groups,

    showgrid=True,

    gridcolor="#DCEEF7",
    gridwidth=1.2,

    showline=True,
    linecolor="#B8DCEB",

    tickfont=dict(size=12),

    zeroline=False
)

# ---------------------------------------
# 16. 세로축 설정
# 100명 단위 구분선
# ---------------------------------------

fig.update_yaxes(

    title_text="인구수 (명)",

    range=[0, y_max],

    dtick=100,

    showgrid=True,

    gridcolor="#E2EDF3",
    gridwidth=0.7,

    showline=True,
    linecolor="#B8DCEB",

    tickformat=",.0f",

    zeroline=True,
    zerolinecolor="#A7D8F0",
    zerolinewidth=1.5
)

# ---------------------------------------
# 17. 그래프 출력
# ---------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------
# 18. 데이터 표 출력
# ---------------------------------------

with st.expander("📋 연령별 상세 인구 데이터 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].map(lambda x: f"{x:,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------
# 19. 안내 문구
# ---------------------------------------

st.divider()

st.caption(
    "📌 데이터 출처: 업로드한 population.csv"
)

st.caption(
    "💡 연령은 10살 단위이며, "
    "100세 이상은 하나의 연령 구간으로 표시됩니다."
)

