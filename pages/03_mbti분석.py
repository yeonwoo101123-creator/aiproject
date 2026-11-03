
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌍",
    layout="wide"
)


# =====================================
# 2. CSV 데이터 불러오기
# =====================================
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types (1).csv"


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    # 열 이름 앞뒤 공백 제거
    data.columns = data.columns.str.strip()

    # 국가명 열 확인
    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    # 국가명 정리
    data["Country"] = (
        data["Country"]
        .astype(str)
        .str.strip()
    )

    data = data.dropna(subset=["Country"])
    data = data[data["Country"] != ""]

    # Country를 제외한 나머지 열은 MBTI 유형
    mbti_columns = [
        column
        for column in data.columns
        if column != "Country"
    ]

    if not mbti_columns:
        raise ValueError(
            "MBTI 유형 열을 찾을 수 없습니다."
        )

    # MBTI 데이터를 숫자로 변환
    for column in mbti_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    return data, mbti_columns


# 파일 존재 여부 확인
if not DATA_FILE.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 "
        "'countriesMBTI_16types (1).csv'를 넣어 주세요."
    )
    st.stop()


# 데이터 불러오기
try:
    df, mbti_columns = load_data(
        str(DATA_FILE)
    )

except Exception as error:
    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )
    st.stop()


# 국가 목록 만들기
countries = sorted(
    df["Country"].dropna().unique().tolist()
)

if not countries:
    st.error("국가 데이터가 없습니다.")
    st.stop()


# =====================================
# 3. 앱 제목
# =====================================
st.title("🌍 세계 MBTI 탐험")

st.subheader(
    "국가별 MBTI 유형의 비율을 알아봐요! 📊"
)

st.write(
    "원하는 국가를 선택하면 "
    "16가지 MBTI 유형의 비율을 "
    "막대그래프로 확인할 수 있어요."
)

st.caption(
    "※ CSV 데이터 기반 분석입니다. "
    "실제 국민 전체의 MBTI 분포를 "
    "보장하는 자료는 아닙니다."
)

st.divider()


# =====================================
# 4. 국가 선택
# =====================================
selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요",
    countries
)


# 선택한 국가의 데이터 가져오기
selected_row = df.loc[
    df["Country"] == selected_country
].iloc[0]

values = selected_row[mbti_columns].dropna()


if values.empty:
    st.warning(
        "선택한 국가에는 표시할 데이터가 없습니다."
    )
    st.stop()


# =====================================
# 5. MBTI 비율 계산 및 정렬
# =====================================
chart_df = values.rename_axis(
    "MBTI"
).reset_index(name="비율")

# 원본 값이 0.0463이라면 4.63%로 변환
chart_df["비율(%)"] = (
    chart_df["비율"] * 100
)

# 높은 비율부터 정렬
chart_df = chart_df.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)


# =====================================
# 6. 그래프 색상 그라데이션 함수
# =====================================
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *rgb
    )


def blend_colors(
    start_color,
    end_color,
    amount
):
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    rgb = tuple(
        round(
            start[i]
            + (end[i] - start[i]) * amount
        )
        for i in range(3)
    )

    return rgb_to_hex(rgb)


# 색상 지정
MINT = "#62DDBB"
SKY_BLUE = "#87CEEB"
PALE_BLUE = "#EAF8FF"


# =====================================
# 7. 순위별 그래프 색상 설정
# =====================================
colors_by_type = {}

count = len(chart_df)

for rank, row in chart_df.iterrows():

    mbti = row["MBTI"]

    # 1위는 민트색
    if rank == 0:
        colors_by_type[mbti] = MINT

    # 2위부터는 하늘색에서 점점 옅어짐
    else:
        denominator = max(count - 2, 1)

        amount = (
            (rank - 1) / denominator
        )

        colors_by_type[mbti] = blend_colors(
            SKY_BLUE,
            PALE_BLUE,
            amount
        )


# =====================================
# 8. 상단 요약 정보
# =====================================
top_type = chart_df.iloc[0]["MBTI"]

top_percent = chart_df.iloc[0]["비율(%)"]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌏 선택한 국가",
        selected_country
    )

with col2:
    st.metric(
        "🏆 비율 1위 MBTI",
        top_type
    )

with col3:
    st.metric(
        "📈 1위 비율",
        f"{top_percent:.2f}%"
    )


# =====================================
# 9. 막대그래프 만들기
# =====================================
# 가로 막대그래프에서 높은 순위가 위에
# 표시되도록 낮은 값부터 배치
plot_df = chart_df.sort_values(
    "비율(%)",
    ascending=True
)

bar_colors = [
    colors_by_type[mbti]
    for mbti in plot_df["MBTI"]
]


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=plot_df["비율(%)"],
        y=plot_df["MBTI"],
        orientation="h",

        # 순위별 색상 적용
        marker=dict(
            color=bar_colors,
            line=dict(width=0)
        ),

        # 막대 끝에 비율 표시
        text=[
            f"{value:.2f}%"
            for value in plot_df["비율(%)"]
        ],

        textposition="outside",
        cliponaxis=False,

        # 마우스를 올리면 상세 정보 표시
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)


# 그래프 디자인
fig.update_layout(
    title=f"{selected_country}의 MBTI 유형별 비율",

    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",

    xaxis=dict(
        rangemode="tozero",
        ticksuffix="%",
        showgrid=True,
        gridcolor="#E8EEF2"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#263238"
    ),

    margin=dict(
        l=25,
        r=65,
        t=65,
        b=45
    ),

    height=650,
    showlegend=False
)


# Streamlit 화면에 그래프 표시
st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 10. 상세 비율 표
# =====================================
with st.expander("📋 MBTI 비율 상세 표 보기"):

    display_df = chart_df[
        ["MBTI", "비율(%)"]
    ].copy()

    display_df.insert(
        0,
        "순위",
        range(1, len(display_df) + 1)
    )

    display_df["비율(%)"] = (
        display_df["비율(%)"].round(2)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 11. 색상 안내
# =====================================
st.divider()

st.markdown(
    """
    ### 🎨 그래프 색상 안내

    - 🟩 **1위:** 민트색
    - 🩵 **2위:** 하늘색
    - 🩵 **3위 이하:** 순위가 낮아질수록
      점점 옅어지는 하늘색

    국가를 바꾸면 해당 국가의 데이터에 맞춰
    순위와 그래프 색상이 자동으로 변경됩니다.
    """
)


# =====================================
# 12. 하단 안내
# =====================================
st.caption(
    "💡 세계 MBTI 탐험 | "
    "Streamlit과 Plotly로 만든 데이터 시각화 앱"
)
