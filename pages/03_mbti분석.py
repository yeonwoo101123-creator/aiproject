
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

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="MBTI별 국가 순위",
    page_icon="🌍",
    layout="wide"
)


# =====================================
# 2. CSV 파일 경로
# pages 폴더의 상위 폴더에 CSV가 있음
# =====================================
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "countriesMBTI_16types (1).csv"
)


# =====================================
# 3. 데이터 불러오기
# =====================================
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    data["Country"] = (
        data["Country"]
        .astype(str)
        .str.strip()
    )

    data = data.dropna(subset=["Country"])
    data = data[data["Country"] != ""]

    mbti_columns = [
        col for col in data.columns
        if col != "Country"
    ]

    if not mbti_columns:
        raise ValueError(
            "MBTI 유형 열을 찾을 수 없습니다."
        )

    for col in mbti_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    return data, mbti_columns


# 파일 확인
if not DATA_FILE.exists():
    st.error(
        f"CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {DATA_FILE}"
    )
    st.stop()


# 데이터 읽기
try:
    df, mbti_types = load_data(str(DATA_FILE))

except Exception as error:
    st.error(f"데이터를 읽을 수 없습니다: {error}")
    st.stop()


# =====================================
# 4. 화면 제목
# =====================================
st.title("🌍 MBTI별 국가 순위")
st.subheader(
    "MBTI를 선택하고 해당 유형의 비율이 높은 국가를 찾아보세요! 📊"
)

st.write(
    "원하는 MBTI를 선택하면 국가별 비율을 계산해 "
    "1위부터 순서대로 막대그래프로 보여 줍니다."
)

st.caption(
    "※ 제공된 CSV 데이터에 기반한 순위이며, "
    "실제 국민 전체의 MBTI 분포를 보장하지 않습니다."
)

st.divider()


# =====================================
# 5. MBTI 선택
# =====================================
selected_mbti = st.selectbox(
    "🧠 MBTI 유형을 선택하세요",
    mbti_types
)


# =====================================
# 6. 선택한 MBTI의 국가별 데이터 만들기
# =====================================
ranking_df = df[
    ["Country", selected_mbti]
].copy()

ranking_df[selected_mbti] = pd.to_numeric(
    ranking_df[selected_mbti],
    errors="coerce"
)

ranking_df = ranking_df.dropna(
    subset=[selected_mbti]
)

# 비율을 백분율로 변환
ranking_df["비율(%)"] = (
    ranking_df[selected_mbti] * 100
)

# 높은 비율부터 정렬
ranking_df = ranking_df.sort_values(
    by="비율(%)",
    ascending=False
).reset_index(drop=True)

# 1위부터 순위 부여
ranking_df.insert(
    0,
    "순위",
    range(1, len(ranking_df) + 1)
)


# =====================================
# 7. 상위 국가 요약
# =====================================
if ranking_df.empty:
    st.warning(
        "선택한 MBTI에 표시할 데이터가 없습니다."
    )
    st.stop()

first_country = ranking_df.iloc[0]["Country"]
first_percent = ranking_df.iloc[0]["비율(%)"]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🧠 선택한 MBTI",
        selected_mbti
    )

with col2:
    st.metric(
        "🏆 1위 국가",
        first_country
    )

with col3:
    st.metric(
        "📈 1위 비율",
        f"{first_percent:.2f}%"
    )


# =====================================
# 8. 그래프에 표시할 국가 수 선택
# =====================================
display_count = st.slider(
    "📊 그래프에 표시할 국가 수",
    min_value=5,
    max_value=min(50, len(ranking_df)),
    value=min(20, len(ranking_df)),
    step=5
)

top_df = ranking_df.head(display_count).copy()


# =====================================
# 9. 순위별 색상 그라데이션
# 1위 민트색, 나머지는 하늘색 계열
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


def blend_colors(start_color, end_color, amount):
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


MINT = "#62DDBB"
SKY_BLUE = "#87CEEB"
PALE_BLUE = "#EAF8FF"

bar_colors = []

for i in range(len(top_df)):

    if i == 0:
        # 1위는 민트색
        bar_colors.append(MINT)

    else:
        # 2위부터 하늘색에서 옅은 색으로
        denominator = max(len(top_df) - 2, 1)
        amount = (i - 1) / denominator

        color = blend_colors(
            SKY_BLUE,
            PALE_BLUE,
            amount
        )

        bar_colors.append(color)


# =====================================
# 10. 가로 막대그래프
# =====================================
# 가로 그래프는 낮은 순위부터 입력해야
# 화면 위쪽에 1위가 나타남
plot_df = top_df.iloc[::-1].copy()
plot_colors = bar_colors[::-1]


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=plot_df["비율(%)"],
        y=plot_df["Country"],
        orientation="h",

        marker=dict(
            color=plot_colors,
            line=dict(width=0)
        ),

        text=[
            f"{value:.2f}%"
            for value in plot_df["비율(%)"]
        ],

        textposition="outside",
        cliponaxis=False,

        customdata=plot_df["순위"],

        hovertemplate=(
            "<b>%{y}</b><br>"
            "순위: %{customdata}위<br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)


fig.update_layout(
    title=f"{selected_mbti} 비율이 높은 국가 TOP {display_count}",

    xaxis_title="MBTI 비율 (%)",
    yaxis_title="국가",

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
        r=70,
        t=65,
        b=45
    ),

    height=max(450, display_count * 28),
    showlegend=False
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 11. 전체 국가 순위표
# =====================================
with st.expander("📋 전체 국가 순위표 보기"):

    table_df = ranking_df[
        ["순위", "Country", "비율(%)"]
    ].copy()

    table_df["비율(%)"] = (
        table_df["비율(%)"].round(2)
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )

    # CSV 다운로드
    csv_data = table_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 국가 순위표 다운로드",
        data=csv_data,
        file_name=f"{selected_mbti}_국가순위.csv",
        mime="text/csv"
    )


# =====================================
# 12. 하단 안내
# =====================================
st.divider()

st.markdown(
    """
    ### 🎨 그래프 색상 안내

    - 🟩 **1위 국가:** 민트색
    - 🩵 **2위 국가:** 하늘색
    - 🩵 **3위 이하:** 순위가 낮아질수록
      점점 옅어지는 하늘색

    MBTI 유형을 바꾸면 국가 순위와 그래프가
    자동으로 변경됩니다.
    """
)

st.caption(
    "💡 세계 MBTI 탐험 | Streamlit + pandas + Plotly"
)

