
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")

st.markdown("""
과거의 실제 기온 데이터를 이용하여 미래의 평균기온을 예측해 봅시다!

선형회귀 알고리즘을 이용해 연도별 기온 변화 추세를 분석합니다.
""")

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    # 현재 py 파일은 pages 폴더에 있고
    # CSV 파일은 그 상위 폴더에 있음
    file_path = (
        Path(__file__).resolve().parent.parent
        / "temperature.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    # CSV 인코딩 확인
    try:
        data = pd.read_csv(
            file_path,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        data = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    # 필요한 열 확인
    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 {col} 열이 없습니다."
            )

    # 날짜 변환 (예: Oct-07)
    data["날짜"] = pd.to_datetime(
        data["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    # 평균기온 숫자로 변환
    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 결측값 제거
    data = data.dropna(
        subset=[
            "연도",
            "월",
            "평균기온(℃)"
        ]
    )

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    return data.sort_values("날짜")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 데이터 정보
# ==========================================
st.subheader("📁 기온 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터 개수",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "데이터 시작 연도",
        f"{df['연도'].min()}년"
    )

with col3:
    st.metric(
        "데이터 마지막 연도",
        f"{df['연도'].max()}년"
    )

st.divider()


# ==========================================
# 4. 사용자 입력
# ==========================================
st.subheader("🔎 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요.",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=1900,
        max_value=2100,
        value=int(df["연도"].max()) + 1,
        step=1
    )

prediction_year = int(prediction_year)

st.divider()


# ==========================================
# 5. 선택한 월의 데이터 추출
# ==========================================
monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values(
    "연도"
)

if len(monthly_data) < 2:
    st.error(
        "선택한 월의 데이터가 부족합니다."
    )
    st.stop()

X = monthly_data[["연도"]]

y = monthly_data["평균기온(℃)"]


# ==========================================
# 6. 선형회귀 모델 학습
# ==========================================
model = LinearRegression()

# 실제 CSV 데이터로 학습
model.fit(X, y)

# 사용자가 선택한 연도 예측
prediction = model.predict(
    pd.DataFrame({
        "연도": [prediction_year]
    })
)[0]

# 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r2 = model.score(X, y)


# ==========================================
# 7. 회귀 직선 계산
# ==========================================
min_year = int(monthly_data["연도"].min())
max_year = int(monthly_data["연도"].max())

line_start = min(
    min_year,
    prediction_year
)

line_end = max(
    max_year,
    prediction_year
)

line_years = list(
    range(line_start, line_end + 1)
)

line_temperatures = model.predict(
    pd.DataFrame({
        "연도": line_years
    })
)


# ==========================================
# 8. 예측 결과 출력
# ==========================================
st.subheader(
    f"📊 {selected_month}월 평균기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
        f"{prediction_year}년"
    )

with col2:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

with col3:
    st.metric(
        "결정계수 R²",
        f"{r2:.3f}"
    )

if prediction_year > max_year:
    st.info(
        f"현재 {max_year}년까지의 실제 데이터를 학습하여 "
        f"{prediction_year}년의 기온을 예측했습니다."
    )

elif prediction_year < min_year:
    st.warning(
        "실제 데이터보다 이전 연도를 예측하고 있습니다. "
        "과거 방향으로 추세선을 연장한 결과입니다."
    )


# ==========================================
# 9. 그래프 그리기
# ==========================================
st.subheader(
    f"📈 {selected_month}월 실제 기온과 예측 기온"
)

fig = go.Figure()

# 실제값과 회귀값의 차이 계산
fitted_values = model.predict(X)

residual_x = []
residual_y = []

for year, actual, fitted in zip(
    monthly_data["연도"],
    y,
    fitted_values
):
    residual_x.extend([
        int(year),
        int(year),
        None
    ])

    residual_y.extend([
        actual,
        fitted,
        None
    ])


# 회색 점선: 잔차
fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="실제값과 회귀값의 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# 파란색 점: 실제 평균기온
fig.add_trace(
    go.Scatter(
        x=monthly_data["연도"],
        y=monthly_data["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2196F3",
            size=9
        ),
        hovertemplate=
        "연도: %{x}년<br>" +
        "실제 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 빨간색 선: 선형회귀 직선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temperatures,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="#FF5252",
            width=3
        ),
        hovertemplate=
        "연도: %{x}년<br>" +
        "회귀값: %{y:.2f}℃<extra></extra>"
    )
)


# 초록색 별표: 최종 예측값
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[prediction],
        mode="markers+text",
        name="예측 기온",
        marker=dict(
            color="#00C853",
            size=16,
            symbol="star"
        ),
        text=[
            f"{prediction:.2f}℃"
        ],
        textposition="top center",
        hovertemplate=
        "예측 연도: %{x}년<br>" +
        "예측 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 그래프 디자인
fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온 분석",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=600,
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    dtick=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. 그래프 범례 설명
# ==========================================
st.markdown("""
### 📌 그래프 읽는 방법

- 🔵 파란색 점: CSV에 저장된 실제 평균기온
- 🔴 빨간색 선: 선형회귀 알고리즘이 계산한 추세선
- 🟢 초록색 별표: 사용자가 입력한 연도의 예측 기온
- 회색 점선: 실제 기온과 회귀 직선 사이의 오차(잔차)
""")


# ==========================================
# 11. 선형회귀 알고리즘 설명
# ==========================================
st.divider()

st.subheader(
    "🧠 선형회귀 알고리즘은 어떻게 작동할까요?"
)

st.markdown("""
### ① 실제 데이터를 학습합니다.

파란색 점은 temperature.csv에 저장된 실제 평균기온입니다.

예를 들어 1월을 선택하면 모든 연도의 1월 평균기온을 가져옵니다.

선형회귀 알고리즘은 연도와 평균기온 사이의 관계를 분석합니다.


### ② 가장 적합한 직선을 찾습니다.

빨간색 선은 선형회귀 알고리즘이 계산한 추세선입니다.

알고리즘은 실제 데이터 점과 직선 사이의 세로 방향 오차를 계산합니다.

그리고 각 오차를 제곱하여 모두 더한 값이 최소가 되도록
직선의 기울기와 절편을 결정합니다.

이 방법을 최소제곱법이라고 합니다.


### ③ 새로운 연도의 기온을 예측합니다.

회귀 직선이 만들어지면 사용자가 입력한 연도를
직선의 식에 대입합니다.

계산된 결과가 그래프의 초록색 별표입니다.


### ④ 회색 점선은 무엇일까요?

회색 점선은 실제 관측 기온과 회귀 직선이 예측한 기온 사이의 차이입니다.

이 차이를 잔차(Residual)라고 합니다.

잔차가 작으면 실제 기온이 회귀 직선에 가깝다는 뜻입니다.
""")


# ==========================================
# 12. 선형회귀 수식
# ==========================================
st.subheader(
    "📐 선형회귀의 수학적 원리"
)

st.latex(
    r"y = ax + b"
)

st.markdown(f"""
- x : 연도
- y : 예측 평균기온
- a : 기울기 ({slope:.4f})
- b : 절편 ({intercept:.2f})

이번에 선택한 {selected_month}월의 회귀식은 다음과 같습니다.
""")

st.latex(
    f"y = {slope:.4f}x + ({intercept:.2f})"
)

if slope > 0:
    st.success(
        "기울기가 양수이므로 분석 기간 동안 "
        "평균기온이 상승하는 선형 추세를 보입니다."
    )

elif slope < 0:
    st.info(
        "기울기가 음수이므로 분석 기간 동안 "
        "평균기온이 하락하는 선형 추세를 보입니다."
    )

else:
    st.info(
        "기울기가 0이므로 연도에 따른 "
        "선형적인 변화가 나타나지 않습니다."
    )


# ==========================================
# 13. 결정계수 설명
# ==========================================
st.subheader(
    "📊 결정계수(R²)란?"
)

st.markdown(f"""
현재 선택한 월의 결정계수는 **{r2:.3f}** 입니다.

결정계수는 회귀 직선이 실제 데이터의 변동을
얼마나 설명하는지 나타내는 통계값입니다.

- 1에 가까울수록 데이터가 직선에 잘 맞습니다.
- 0에 가까울수록 직선으로 설명되는 변동이 적습니다.
- 결정계수가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
""")


# ==========================================
# 14. 주의사항
# ==========================================
st.divider()

st.caption("""
※ 본 프로그램은 CSV 파일에 포함된 실제 평균기온 데이터만 학습합니다.

※ 선형회귀는 과거 데이터의 선형적인 변화 추세를 이용합니다.

※ 계절 변화, 기후 변화, 대기 순환 등 복잡한 기상 요인은
별도로 반영하지 않습니다.

※ 따라서 예측 결과는 실제 미래 기온을 보장하지 않는
통계적 추정값입니다.

🌡️ 기온 데이터 분석 프로젝트
""")
