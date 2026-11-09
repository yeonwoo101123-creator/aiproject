
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =========================================
# 1. 페이지 설정
# =========================================
st.set_page_config(
    page_title="서울 기온 데이터 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 데이터 분석")
st.write("서울의 기온 변화를 다양한 그래프로 분석해 보세요!")

st.divider()


# =========================================
# 2. CSV 파일 불러오기
# =========================================
@st.cache_data
def load_data():

    # 현재 파이썬 파일은 pages 폴더
    # CSV 파일은 상위 폴더에 있음
    current_dir = Path(__file__).resolve().parent
    csv_path = current_dir.parent / "temperature.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"temperature.csv 파일을 찾을 수 없습니다.\n{csv_path}"
        )

    # 한글 인코딩 처리
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
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV에 {col} 컬럼이 없습니다."
            )

    # =====================================
    # 3. 월과 연도 추출
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

    def convert_year(value):

        if pd.isna(value):
            return None

        value = str(value)

        if len(value) == 4:
            return int(value)

        year = int(value)

        # 두 자리 연도 변환
        if year <= 68:
            return 2000 + year
        else:
            return 1900 + year

    df["연도"] = parts[1].apply(convert_year)

    # =====================================
    # 4. 숫자형 데이터 변환
    # =====================================
    temp_columns = [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temp_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 분석에 필요한 데이터만 정리
    df = df.dropna(
        subset=["연도", "월"]
    ).copy()

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    df = df.sort_values(
        ["연도", "월"]
    )

    return df


# =========================================
# 5. 데이터 불러오기
# =========================================
try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# =========================================
# 6. 분석 정보
# =========================================
years = sorted(df["연도"].unique())

month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

st.subheader("📊 데이터 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "분석 시작 연도",
        f"{min(years)}년"
    )

with col3:
    st.metric(
        "분석 마지막 연도",
        f"{max(years)}년"
    )


# =========================================
# 그래프 1
# 서울의 월별 평균기온
# =========================================
st.divider()

st.header("① 서울의 월별 평균기온")
st.write(
    "전체 관측 기간의 데이터를 월별로 평균하여 "
    "1월부터 12월까지의 기온을 비교합니다."
)

monthly_avg = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_names,
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#16A085",
            width=3
        ),
        marker=dict(size=9)
    )
)

fig1.update_layout(
    title=dict(
        text="서울 월별 평균기온",
        x=0.5
    ),
    xaxis_title="월",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# =========================================
# 그래프 2
# 연도별 최고기온과 최저기온
# =========================================
st.divider()

st.header("② 연도별 최고기온과 최저기온")
st.write(
    "각 연도에서 관측된 가장 높은 기온과 "
    "가장 낮은 기온을 비교합니다."
)

yearly_temp = (
    df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

fig2 = go.Figure()

# 최고기온 - 빨간색
fig2.add_trace(
    go.Scatter(
        x=yearly_temp["연도"],
        y=yearly_temp["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="red",
            width=3
        ),
        marker=dict(size=6)
    )
)

# 최저기온 - 하늘색
fig2.add_trace(
    go.Scatter(
        x=yearly_temp["연도"],
        y=yearly_temp["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="skyblue",
            width=3
        ),
        marker=dict(size=6)
    )
)

fig2.update_layout(
    title=dict(
        text="연도별 최고기온과 최저기온",
        x=0.5
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
    template="plotly_white",
    height=500,
    hovermode="x unified"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# =========================================
# 그래프 3
# 두 연도의 월별 평균기온 비교
# =========================================
st.divider()

st.header("③ 두 연도의 월별 기온 비교")

st.write(
    "비교하고 싶은 연도 2개를 선택하세요. "
    "두 연도의 1월부터 12월까지 평균기온을 비교합니다."
)

if len(years) >= 2:

    # 최근 2개 연도를 기본 선택
    default_years = years[-2:]

    selected_years = st.multiselect(
        "비교할 연도 2개를 선택하세요.",
        options=years,
        default=default_years,
        max_selections=2,
        format_func=lambda x: f"{x}년"
    )

    if len(selected_years) == 2:

        selected_df = df[
            df["연도"].isin(selected_years)
        ].copy()

        compare_data = (
            selected_df.groupby(
                ["연도", "월"]
            )["평균기온(℃)"]
            .mean()
            .reset_index()
        )

        fig3 = go.Figure()

        colors = [
            "#3498DB",
            "#E67E22"
        ]

        for i, year in enumerate(selected_years):

            year_data = compare_data[
                compare_data["연도"] == year
            ].set_index("월")

            values = (
                year_data["평균기온(℃)"]
                .reindex(range(1, 13))
            )

            fig3.add_trace(
                go.Scatter(
                    x=month_names,
                    y=values.values,
                    mode="lines+markers",
                    name=f"{year}년",
                    line=dict(
                        color=colors[i],
                        width=3
                    ),
                    marker=dict(size=8),
                    connectgaps=False
                )
            )

        fig3.update_layout(
            title=dict(
                text=(
                    f"{selected_years[0]}년과 "
                    f"{selected_years[1]}년 월별 평균기온 비교"
                ),
                x=0.5
            ),
            xaxis_title="월",
            yaxis_title="평균기온 (℃)",
            legend=dict(
                title="비교 연도",
                orientation="h",
                y=1.12,
                x=0.5,
                xanchor="center"
            ),
            template="plotly_white",
            height=500,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        st.subheader("📋 두 연도 기온 비교표")

        comparison_table = compare_data.pivot(
            index="월",
            columns="연도",
            values="평균기온(℃)"
        )

        comparison_table.index = [
            f"{month}월"
            for month in comparison_table.index
        ]

        st.dataframe(
            comparison_table.round(2),
            use_container_width=True
        )

    else:
        st.info("비교할 연도를 정확히 2개 선택해 주세요.")

else:
    st.warning("비교할 수 있는 연도가 2개 이상 필요합니다.")


# =========================================
# 7. 원본 데이터 확인
# =========================================
st.divider()

with st.expander("📂 원본 데이터 확인하기"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================================
# 8. 분석 데이터 다운로드
# =========================================
st.divider()

csv_data = df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 데이터 다운로드",
    data=csv_data,
    file_name="서울_기온분석.csv",
    mime="text/csv"
)

st.success("🎉 서울 기온 데이터 분석이 완료되었습니다!")

st.caption(
    "서울 기온 데이터 분석 | Pandas + Plotly + Streamlit"
)

