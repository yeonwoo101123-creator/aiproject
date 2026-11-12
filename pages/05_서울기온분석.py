
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =========================================
# 1. 페이지 설정
# =========================================
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write(
    "월을 선택하면 연도별 최고기온과 최저기온을 "
    "꺾은선 그래프로 비교할 수 있습니다."
)

# =========================================
# 2. CSV 파일 불러오기
# =========================================
@st.cache_data
def load_data():

    # 현재 py 파일은 pages 폴더에 있음
    # CSV 파일은 pages의 상위 폴더에 있음
    current_dir = Path(__file__).resolve().parent

    csv_path = current_dir.parent / "temperature.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {csv_path}"
        )

    # 한글 인코딩 자동 처리
    df = None

    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            df = pd.read_csv(
                csv_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인해 주세요."
        )

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"'{col}' 컬럼이 CSV에 없습니다."
            )

    # =====================================
    # 3. 날짜 데이터 처리
    # =====================================
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    df["일시"] = df["일시"].astype(str).str.strip()

    parts = df["일시"].str.extract(
        r"^([A-Za-z]{3})-(\d{2}|\d{4})$"
    )

    df["월"] = parts[0].str.title().map(month_dict)

    years = []
    previous_year = None
    previous_month = None

    for month_name, year_text in zip(
        parts[0], parts[1]
    ):

        if pd.isna(month_name) or pd.isna(year_text):
            years.append(None)
            continue

        month = month_dict.get(month_name.title())

        if month is None:
            years.append(None)
            continue

        year_number = int(year_text)

        if len(year_text) == 4:
            year = year_number

        elif previous_year is None:
            year = 1900 + year_number

        else:
            year = (
                previous_year // 100
            ) * 100 + year_number

            if (year, month) <= (
                previous_year, previous_month
            ):
                year += 100

        years.append(year)

        previous_year = year
        previous_month = month

    df["연도"] = years

    # =====================================
    # 4. 기온 숫자형 변환
    # =====================================
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
    ).copy()

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df


# =========================================
# 5. 데이터 불러오기
# =========================================
try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# =========================================
# 6. 월 선택
# =========================================
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
    format_func=lambda x: month_names[x]
)


# =========================================
# 7. 선택한 월의 데이터 분석
# =========================================
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


# =========================================
# 8. 꺾은선 그래프
# =========================================
if yearly_data.empty:

    st.warning(
        "선택한 월에 분석할 데이터가 없습니다."
    )

else:

    fig = go.Figure()

    # 최고기온: 빨간색
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
            marker=dict(size=6)
        )
    )

    # 최저기온: 하늘색
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
            marker=dict(size=6)
        )
    )

    # 그래프 디자인
    fig.update_layout(
        title=dict(
            text="월별 기온분석",
            x=0.5,
            xanchor="center"
        ),

        xaxis_title="연도",
        yaxis_title="온도 (℃)",

        legend=dict(
            title="범례",
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center"
        ),

        hovermode="x unified",

        template="plotly_white",

        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================
# 9. 연도별 기온 데이터 표
# =========================================
st.divider()

st.subheader("📋 연도별 기온 데이터")

st.dataframe(
    yearly_data,
    use_container_width=True,
    hide_index=True
)


# =========================================
# 10. 기온 분석 결과
# =========================================
st.divider()

st.subheader("🔍 기온 분석 결과")

if not yearly_data.empty:

    col1, col2 = st.columns(2)

    with col1:

        highest = yearly_data[
            "최고기온(℃)"
        ].max()

        st.metric(
            "가장 높은 최고기온",
            f"{highest:.1f}℃"
        )

    with col2:

        lowest = yearly_data[
            "최저기온(℃)"
        ].min()

        st.metric(
            "가장 낮은 최저기온",
            f"{lowest:.1f}℃"
        )

# =========================================
# 11. CSV 다운로드
# =========================================
st.divider()

csv_data = yearly_data.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 결과 다운로드",
    data=csv_data,
    file_name="월별_기온분석.csv",
    mime="text/csv"
)

st.success("🎉 월별 기온분석이 완료되었습니다!")

