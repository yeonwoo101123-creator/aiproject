
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="KBL 선수 비교",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 KBL 선수 비교 사이트")
st.caption("두 선수를 선택하고 시즌 기록을 비교해 보세요!")


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# 현재 파이썬 파일은 pages 폴더 안에 있음
# CSV 파일은 pages 폴더의 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "KBL_2026-27_선수기록_최종.csv"


# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        CSV_PATH,
        encoding="utf-8-sig"
    )

    # 숫자 데이터 변환
    numeric_columns = [
        "출전경기",
        "평균출전시간(분)",
        "평균득점",
        "평균리바운드",
        "평균어시스트",
        "평균3점슛성공",
        "야투성공률(%)",
        "평균스틸",
        "평균블록"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["선수명"] = df["선수명"].astype(str).str.strip()
    df["구단"] = df["구단"].astype(str).str.strip()

    return df


# CSV 파일 존재 여부 확인

if not CSV_PATH.exists():

    st.error("CSV 파일을 찾을 수 없습니다.")

    st.info(
        "CSV 파일이 프로젝트 최상위 폴더에 있는지 확인하세요."
    )

    st.stop()


try:
    df = load_data()

except Exception as e:

    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

    st.stop()


# ==========================================
# 4. 선수 선택
# ==========================================

st.subheader("👥 비교할 선수 선택")

player_names = sorted(
    df["선수명"].unique().tolist()
)

col1, col2 = st.columns(2)

with col1:

    player1_name = st.selectbox(
        "첫 번째 선수",
        player_names,
        key="player1"
    )


with col2:

    # 첫 번째 선수와 다른 선수만 표시
    player2_options = [
        name for name in player_names
        if name != player1_name
    ]

    player2_name = st.selectbox(
        "두 번째 선수",
        player2_options,
        key="player2"
    )


# 선택한 선수의 데이터 가져오기

player1 = df[
    df["선수명"] == player1_name
].iloc[0]

player2 = df[
    df["선수명"] == player2_name
].iloc[0]


# ==========================================
# 5. 선수 소속 정보 출력
# ==========================================

st.divider()

st.subheader("🏀 선수 기본 정보")

info1, info2 = st.columns(2)

with info1:

    st.markdown(f"### 🔴 {player1['선수명']}")

    st.success(
        f"소속 구단: {player1['구단']}"
    )

    st.write(
        f"포지션: {player1['포지션']}"
    )

    st.write(
        f"시즌: {player1['기준시즌']}"
    )


with info2:

    st.markdown(f"### 🔴 {player2['선수명']}")

    st.success(
        f"소속 구단: {player2['구단']}"
    )

    st.write(
        f"포지션: {player2['포지션']}"
    )

    st.write(
        f"시즌: {player2['기준시즌']}"
    )


# ==========================================
# 6. 비교할 기록 선택
# ==========================================

st.divider()

st.subheader("📊 선수 기록 비교")

stat_options = {

    "평균 득점": ("평균득점", "점"),

    "평균 리바운드": ("평균리바운드", "개"),

    "평균 어시스트": ("평균어시스트", "개"),

    "평균 출전 시간": ("평균출전시간(분)", "분"),

    "평균 3점슛 성공": ("평균3점슛성공", "개"),

    "야투 성공률": ("야투성공률(%)", "%"),

    "평균 스틸": ("평균스틸", "개"),

    "평균 블록": ("평균블록", "개"),

    "출전 경기": ("출전경기", "경기")

}


selected_stat = st.selectbox(
    "비교할 기록을 선택하세요.",
    list(stat_options.keys())
)


stat_column, unit = stat_options[selected_stat]


value1 = player1[stat_column]

value2 = player2[stat_column]


# ==========================================
# 7. 그래프 만들기
# ==========================================

if pd.isna(value1) or pd.isna(value2):

    st.warning("선택한 기록에 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 첫 번째 선수
    fig.add_trace(

        go.Bar(

            x=[player1_name],

            y=[value1],

            name=player1_name,

            marker_color="#E53935",

            text=[f"{value1:g}{unit}"],

            textposition="outside"

        )

    )


    # 두 번째 선수
    fig.add_trace(

        go.Bar(

            x=[player2_name],

            y=[value2],

            name=player2_name,

            marker_color="#FF8A80",

            text=[f"{value2:g}{unit}"],

            textposition="outside"

        )

    )


    # 그래프 디자인
    fig.update_layout(

        title=f"{selected_stat} 비교",

        xaxis_title="선수",

        yaxis_title=f"{selected_stat} ({unit})",

        barmode="group",

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(
            family="Arial",
            size=14
        ),

        legend_title_text="선수",

        margin=dict(
            t=70,
            b=40,
            l=30,
            r=30
        )

    )

    fig.update_yaxes(
        rangemode="tozero",
        gridcolor="#EEEEEE"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# 8. 두 선수의 전체 기록 비교표
# ==========================================

st.divider()

st.subheader("📋 두 선수의 전체 기록")

display_columns = [

    "구단",

    "선수명",

    "포지션",

    "출전경기",

    "평균출전시간(분)",

    "평균득점",

    "평균리바운드",

    "평균어시스트",

    "평균3점슛성공",

    "야투성공률(%)",

    "평균스틸",

    "평균블록"

]


comparison_table = df[
    df["선수명"].isin([
        player1_name,
        player2_name
    ])
][display_columns]


st.dataframe(
    comparison_table,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 9. 마무리 안내
# ==========================================

st.divider()

st.caption(
    "🏀 KBL 선수 비교 사이트 | "
    "CSV에 저장된 시즌 기록을 기준으로 비교합니다."
)

