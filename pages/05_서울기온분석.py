
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

# =====================================
# 2. CSV 파일 불러오기
# =====================================
@st.cache_data
def load_data():

    base_path = Path(__file__).resolve().parent

    file_path = base_path / "temperature.csv"

    if not file_path.exists():
        file_path = base_path.parent / "temperature.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    # 한글 인코딩 처리
    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"필요한 컬럼이 없습니다: {missing_columns}"
        )

    # 날짜 처리
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    df["일시"] = df["일시"].astype(str).str.strip()

    # 원본 데이터의 월과 연도 분리
    parts = df["일시"].str.extract(
        r"^([A-Za-z]{3})-(\d{2}|\d{4})$"
    )

    df["월"] = parts[0].map(months)

    # 연도는 데이터가 시간순으로 정렬되어 있다는 전제에서 복원
    years = []
    previous_year = None
    previous_month = None

    for month_name, year_text in zip(parts[0], parts[1]):

        if pd.isna(month_name) or pd.isna(year_text):
            years.append(None)
            continue

        month = months.get(month_name)

        if month is None:
            years.append(None)
            continue

        year_number = int(year_text)

        if len(year_text) == 4:
            year = year_number
        elif previous_year is None:
            year = 1900 + year_number
        else:
            year = (previous_year // 100) * 100 + year_number

            if (year, month) <= (
                previous_year, previous_month
            ):
                year += 100

        years.append(year)
        previous_year = year
        previous_month = month

    df["연도"] = years

    # 기온을 숫자로 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"],
        errors="coerce"
    )

    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "연도",
            "월",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df


# =====================================
# 3. 데이터 불러오기
# =====================================
try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# =====================================
# 4. 월 선택
# =====================================
st.subheader("📅 분석할 월 선택")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "원하는 월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x],
    index=0
)


# =====================================
# 5. 선택한 월의 데이터 추출
# =====================================
month_df = df[
    df["월"] == selected_month
].copy()

# 연도별 최고기온과 최저기온 계산
yearly_data = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

st.divider()

st.subheader(
    f"📊 {month_names[selected_month]} 월별 기온분석"
)


# =====================================
# 6. 꺾은선 그래프
# =====================================
if yearly_data.empty:

    st.warning("선택한 월에 분석할 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 그래프 - 빨간색
    fig.add_trace(
        go.Scatter(
            x=yearly_data["연도"],
            y=yearly_data["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="red",
                width=3
            ),
            marker=dict(size=6),
            connectgaps=False
        )
    )

    # 최저기온 그래프 - 하늘색
    fig.add_trace(
        go.Scatter(
            x=yearly_data["연도"],
            y=yearly_data["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="skyblue",
                width=3
            ),
            marker=dict(size=6),
            connectgaps=False
        )
    )

    # 그래프 제목 및 축 설정
    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },

        xaxis_title="연도",
        yaxis_title="온도 (℃)",

        xaxis=dict(
            tickmode="linear",
            dtick=10
        ),

        legend=dict(
            title="범례",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),

        hovermode="x unified",

        template="plotly_white",

        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================
# 7. 데이터 표
# =====================================
st.divider()

st.subheader("📋 연도별 기온 데이터")

display_df = yearly_data.rename(
    columns={
        "연도": "연도",
        "최고기온(℃)": "최고기온(℃)",
        "최저기온(℃)": "최저기온(℃)"
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =====================================
# 8. 요약 정보
# =====================================
st.divider()

st.subheader("🔍 기온 분석 결과")

col1, col2 = st.columns(2)

with col1:
    highest = yearly_data["최고기온(℃)"].max()

    st.metric(
        "선택한 월의 가장 높은 기온",
        f"{highest:.1f}℃"
    )

with col2:
    lowest = yearly_data["최저기온(℃)"].min()

    st.metric(
        "선택한 월의 가장 낮은 기온",
        f"{lowest:.1f}℃"
    )

st.success("🎉 기온 분석이 완료되었습니다!")

st.caption(
    "Pandas와 Plotly를 활용한 기온 데이터 분석"
)
