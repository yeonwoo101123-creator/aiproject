
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)


# =====================================
# 2. CSV 파일 경로 설정
# pages 폴더의 상위 폴더에서 CSV 찾기
# =====================================
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "countriesMBTI_16types (1).csv"
)


# =====================================
# 3. CSV 데이터 불러오기
# =====================================
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    # 열 이름의 공백 제거
    data.columns = data.columns.str.strip()

    # 국가명 열 확인
    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 'Country' 열이 없습니다."
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

    # MBTI 값을 숫자로 변환
    for column in mbti_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    return data, mbti_columns


# CSV 파일 존재 여부 확인
if not DATA_FILE.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        f"찾는 경로: {DATA_FILE}\n\n"
        "CSV 파일이 프로젝트 상위 폴더에 있는지 "
        "그리고 파일 이름이 정확한지 확인해 주세요."
    )
    st.stop()


# 데이터 읽기
try:
    df, mbti_columns = load_data(str(DATA_FILE))

except Exception as error:
    st.error(
        f"CSV 데이터를 읽는 중 오류가 발생했습니다: {error}"
    )
    st.stop()


# 국가 목록 만들기
countries = sorted(
    df["Country"].dropna().unique().tolist()
)

if not countries:
    st.error("CSV 파일에 국가 데이터가 없습니다.")
    st.stop()


# =====================================
# 4. 페이지 제목
# =====================================
st.title("🌍 국가별 MBTI 탐험")
st.subheader(
    "국가를 선택하고 16가지 MBTI 비율을 비교해 보세요! 📊"
)

st.caption(
    "CSV 데이터 기반 시각화입니다. "
    "실제 국민 전체의 MBTI 분포를 보장하지는 않습니다."
)

st.divider()


# =====================================
# 5. 국가 선택
# =====================================
selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요",
    countries
)


# 선택 국가의 데이터 가져오기
selected_row = df.loc[
    df["Country"] == selected_country
].iloc[0]

values = selected_row[mbti_columns].dropna()


if values.empty:
    st.warning(
        "선택한 국가에 표시할 MBTI 데이터가 없습니다."
    )
    st.stop()


# =====================================
# 6. 비율 계산 및 내림차순 정렬
# =====================================
chart_df = (
    values.rename_axis("MBTI")
    .reset_index(name="비율")
)

# 예: 0.0463 → 4.63%
chart_df["비율(%)"] = chart_df["비율"] * 100

chart_df = chart_df.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)


# =====================================
# 7. 색상 변환 함수
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


# =====================================
# 8. 순위별 색상 지정
# =====================================
MINT = "#62DDBB"
SKY_BLUE = "#87CEEB"
PALE_BLUE = "#EAF8FF"

colors_by_type = {}
count = len(chart_df)

for rank, row in chart_df.iterrows():
    mbti = row["MBTI"]

    # 1위: 민트색
    if rank == 0:
        colors_by_type[mbti] = MINT

    # 2위 이하: 하늘색에서 옅은 하늘색으로
    else:
        denominator = max(count - 2, 1)
        amount = (rank - 1) / denominator

        colors_by_type[mbti] = blend_colors(
            SKY_BLUE,
            PALE_BLUE,
            amount
        )


# =====================================
# 9. 상단 요약 카드
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
# 10. 막대그래프 만들기
# =====================================
# 가로 막대그래프에서 1위가 위에 나타나도록
# 낮은 비율부터 그래프에 전달
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
# 11. MBTI 상세 표
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
# 12. 색상 안내
# =====================================
st.divider()

st.markdown(
    """
    ### 🎨 그래프 색상 안내

    - 🟩 **1위:** 민트색
    - 🩵 **2위:** 하늘색
    - 🩵 **3위 이하:** 순위가 낮아질수록
      점점 옅어지는 하늘색

    국가를 바꾸면 해당 국가의 MBTI 순위에 맞춰
    그래프와 색상이 자동으로 변경됩니다.
    """
)


# =====================================
# 13. 하단 안내
# =====================================
st.caption(
    "💡 세계 MBTI 탐험 | "
    "Streamlit + pandas + Plotly"
)

