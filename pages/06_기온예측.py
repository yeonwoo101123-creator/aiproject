
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)


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

이번 프로그램에서는 세 가지 회귀 알고리즘을 사용합니다.

- 선형회귀
- 랜덤 포레스트 회귀
- 그래디언트 부스팅 회귀

같은 데이터를 학습해도 알고리즘에 따라 예측 결과가 어떻게 달라지는지 비교해 보세요!
""")

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    # py 파일은 pages 폴더
    # CSV 파일은 상위 폴더
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
                f"CSV 파일에 '{col}' 열이 없습니다."
            )

    # 날짜 변환
    data["날짜"] = pd.to_datetime(
        data["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    # 기온 숫자 변환
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


# ==========================================
# 5. 회귀 알고리즘 선택
# ==========================================
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = {
    "선형회귀": "Linear Regression",
    "랜덤 포레스트 회귀": "Random Forest Regression",
    "그래디언트 부스팅 회귀": "Gradient Boosting Regression"
}

selected_algorithm = st.selectbox(
    "사용할 회귀 알고리즘을 선택하세요.",
    list(algorithm_names.keys())
)

st.info(
    f"현재 선택한 알고리즘: {selected_algorithm}"
)

st.divider()


# ==========================================
# 6. 선택한 월의 데이터 추출
# ==========================================
monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values(
    "연도"
)

if len(monthly_data) < 2:
    st.error(
        "선택한 월의 데이터가 부족하여 분석할 수 없습니다."
    )
    st.stop()

X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]


# ==========================================
# 7. 세 가지 회귀 모델 생성
# ==========================================
models = {

    # ① 선형회귀
    "선형회귀": LinearRegression(),

    # ② 랜덤 포레스트 회귀
    "랜덤 포레스트 회귀": RandomForestRegressor(
        n_estimators=300,
        max_depth=3,
        random_state=42
    ),

    # ③ 그래디언트 부스팅 회귀
    "그래디언트 부스팅 회귀": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        loss="squared_error",
        random_state=42
    )
}


# ==========================================
# 8. 세 가지 모델 학습 및 예측
# ==========================================
results = {}

for name, model in models.items():

    # 실제 CSV 데이터로 학습
    model.fit(X, y)

    # 사용자가 입력한 연도 예측
    predicted_temperature = model.predict(
        pd.DataFrame({
            "연도": [prediction_year]
        })
    )[0]

    # 학습 데이터에 대한 결정계수
    r2 = model.score(X, y)

    # 학습 데이터의 예측값
    fitted_values = model.predict(X)

    results[name] = {
        "model": model,
        "prediction": float(predicted_temperature),
        "r2": float(r2),
        "fitted_values": fitted_values
    }


# ==========================================
# 9. 선택한 알고리즘의 결과
# ==========================================
selected_result = results[selected_algorithm]

prediction = selected_result["prediction"]
selected_r2 = selected_result["r2"]

st.subheader(
    f"📊 {selected_month}월 예측 결과"
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
        f"{selected_r2:.3f}"
    )

if prediction_year > int(monthly_data["연도"].max()):
    st.info(
        "미래 연도를 예측하고 있습니다. "
        "실제 데이터의 마지막 연도 이후는 통계적 추정값입니다."
    )

elif prediction_year < int(monthly_data["연도"].min()):
    st.warning(
        "실제 데이터보다 이전 연도를 예측하고 있습니다."
    )


# ==========================================
# 10. 세 가지 알고리즘 예측값 비교
# ==========================================
st.divider()

st.subheader("🏆 세 가지 알고리즘 예측값 비교")

comparison_data = []

for name, result in results.items():

    comparison_data.append({
        "회귀 알고리즘": name,
        "예측 평균기온(℃)": round(
            result["prediction"], 2
        ),
        "결정계수(R²)": round(
            result["r2"], 3
        )
    })

comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

predictions = [
    result["prediction"]
    for result in results.values()
]

st.write(
    f"**세 알고리즘의 예측값 차이: "
    f"{max(predictions) - min(predictions):.2f}℃**"
)

st.caption(
    "결정계수는 각 모델이 학습 데이터에 얼마나 적합한지 나타냅니다. "
    "학습 데이터에서 높은 결정계수가 미래 예측의 정확도를 보장하지는 않습니다."
)


# ==========================================
# 11. 그래프에 사용할 연도 생성
# ==========================================
min_year = int(monthly_data["연도"].min())
max_year = int(monthly_data["연도"].max())

line_start = min(min_year, prediction_year)
line_end = max(max_year, prediction_year)

line_years = list(
    range(line_start, line_end + 1)
)

line_X = pd.DataFrame({
    "연도": line_years
})


# ==========================================
# 12. 그래프 그리기
# ==========================================
st.divider()

st.subheader(
    f"📈 {selected_month}월 회귀 알고리즘별 비교 그래프"
)

fig = go.Figure()


# ------------------------------------------
# 실제 평균기온
# ------------------------------------------
fig.add_trace(
    go.Scatter(
        x=monthly_data["연도"],
        y=monthly_data["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2196F3",
            size=10
        ),
        hovertemplate=
        "연도: %{x}년<br>" +
        "실제 기온: %{y:.2f}℃<extra></extra>"
    )
)


# ------------------------------------------
# 알고리즘별 회귀 직선 및 예측값
# ------------------------------------------
colors = {
    "선형회귀": "#FF5252",
    "랜덤 포레스트 회귀": "#00A878",
    "그래디언트 부스팅 회귀": "#9C27B0"
}

for name, result in results.items():

    model = result["model"]

    # 전체 연도의 예측값
    line_predictions = model.predict(line_X)

    # 선택한 알고리즘은 굵게 표시
    if name == selected_algorithm:
        line_width = 4
        line_dash = "solid"
    else:
        line_width = 2
        line_dash = "dash"

    fig.add_trace(
        go.Scatter(
            x=line_years,
            y=line_predictions,
            mode="lines",
            name=name,
            line=dict(
                color=colors[name],
                width=line_width,
                dash=line_dash
            ),
            hovertemplate=
            "연도: %{x}년<br>" +
            "예측 기온: %{y:.2f}℃<extra></extra>"
        )
    )

    # 각 알고리즘의 최종 예측 지점
    fig.add_trace(
        go.Scatter(
            x=[prediction_year],
            y=[result["prediction"]],
            mode="markers",
            name=f"{name} 예측값",
            marker=dict(
                color=colors[name],
                size=13,
                symbol="star"
            ),
            hovertemplate=
            f"알고리즘: {name}<br>" +
            "예측 연도: %{x}년<br>" +
            "예측 기온: %{y:.2f}℃<extra></extra>"
        )
    )


# ------------------------------------------
# 선택한 알고리즘의 잔차 표시
# ------------------------------------------
selected_fitted = selected_result["fitted_values"]

residual_x = []
residual_y = []

for year, actual, fitted in zip(
    monthly_data["연도"],
    y,
    selected_fitted
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

fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="선택 모델의 잔차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# ------------------------------------------
# 그래프 디자인
# ------------------------------------------
fig.update_layout(
    title=(
        f"{selected_month}월 실제 평균기온과 "
        "알고리즘별 예측 비교"
    ),
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    template="plotly_white",
    height=650,
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
# 13. 그래프 읽는 방법
# ==========================================
st.markdown("""
### 📌 그래프 읽는 방법

- 🔵 파란색 점: CSV에 저장된 실제 평균기온
- 🔴 빨간색 선: 선형회귀 예측 추세
- 🟢 초록색 선: 랜덤 포레스트 예측 추세
- 🟣 보라색 선: 그래디언트 부스팅 예측 추세
- ⭐ 별표: 각 알고리즘의 최종 예측 기온
- 회색 점선: 선택한 알고리즘의 실제값과 회귀값 사이의 잔차

선택한 알고리즘은 굵은 선으로 강조됩니다.
""")


# ==========================================
# 14. 알고리즘별 작동 원리
# ==========================================
st.divider()

st.subheader("🧠 세 가지 회귀 알고리즘의 작동 원리")

with st.expander("① 선형회귀 (Linear Regression)", expanded=True):

    st.markdown("""
    **어떻게 작동할까요?**

    1. 과거 연도와 평균기온 데이터를 수집합니다.
    2. 실제 데이터와 가장 잘 맞는 직선을 찾습니다.
    3. 직선의 기울기와 절편을 계산합니다.
    4. 새로운 연도를 직선의 식에 넣어 기온을 예측합니다.

    **핵심 특징**

    - 직선 형태의 추세를 학습합니다.
    - 기울기가 양수이면 상승 경향, 음수이면 하락 경향입니다.
    - 과거의 선형적인 추세를 미래로 연장할 수 있습니다.
    """)

    st.latex(r"y = ax + b")

    st.markdown("""
    - a: 기울기
    - b: 절편
    - x: 연도
    - y: 예측 평균기온
    """)


with st.expander("② 랜덤 포레스트 회귀 (Random Forest Regression)"):

    st.markdown("""
    **어떻게 작동할까요?**

    1. 학습 데이터를 무작위로 추출하여 여러 학습용 데이터를 만듭니다.
    2. 각각의 데이터로 여러 결정 트리를 학습합니다.
    3. 각각의 트리가 기온을 예측합니다.
    4. 여러 트리의 예측 결과를 평균하여 최종 기온을 계산합니다.

    **핵심 특징**

    - 여러 개의 결정 트리를 사용합니다.
    - 데이터의 비선형적인 관계도 학습할 수 있습니다.
    - 여러 트리의 결과를 평균하여 예측합니다.
    - 학습 범위 밖의 미래를 예측할 때는 일반적으로 끝부분의 예측값이 유지되는 형태가 나타납니다.
    """)

    st.latex(
        r"\hat{y} = \frac{1}{N}\sum_{i=1}^{N}T_i(x)"
    )

    st.markdown("""
    - N: 결정 트리의 개수
    - T: 각각의 결정 트리 예측값
    """)


with st.expander("③ 그래디언트 부스팅 회귀 (Gradient Boosting Regression)"):

    st.markdown("""
    **어떻게 작동할까요?**

    1. 첫 번째 모델이 기온을 예측합니다.
    2. 실제 기온과 예측 기온의 차이를 계산합니다.
    3. 다음 모델은 앞선 모델이 잘 맞히지 못한 오차를 학습합니다.
    4. 이러한 과정을 반복하여 여러 모델의 결과를 결합합니다.

    **핵심 특징**

    - 여러 개의 결정 트리를 순차적으로 학습합니다.
    - 앞선 모델의 오차를 보완합니다.
    - 복잡한 데이터 관계를 학습할 수 있습니다.
    - 학습 범위 밖으로 나가면 과거 추세를 계속 연장하지 못할 수 있습니다.
    """)

    st.latex(
        r"F_m(x)=F_{m-1}(x)+\eta h_m(x)"
    )

    st.markdown("""
    - F: 현재까지 결합된 예측 모델
    - h: 새롭게 학습한 결정 트리
    - η: 학습률
    - m: 학습 단계
    """)


# ==========================================
# 15. 현재 선택된 알고리즘 설명
# ==========================================
st.divider()

st.subheader("🔍 내가 선택한 알고리즘 분석")

algorithm_explanations = {

    "선형회귀": """
    선형회귀는 전체 데이터의 직선적인 변화 경향을 분석합니다.
    과거의 상승 또는 하락 추세를 이용하여 미래 기온을 예측합니다.
    """,

    "랜덤 포레스트 회귀": """
    랜덤 포레스트는 여러 결정 트리의 예측 결과를 평균합니다.
    각각의 트리가 서로 다른 데이터 패턴을 학습하므로
    직선이 아닌 다양한 형태의 관계를 표현할 수 있습니다.
    """,

    "그래디언트 부스팅 회귀": """
    그래디언트 부스팅은 이전 모델의 오차를 다음 모델이 보완합니다.
    여러 모델을 순서대로 결합하여 복잡한 데이터 패턴을 학습합니다.
    """
}

st.info(
    f"**{selected_algorithm}**\n\n"
    + algorithm_explanations[selected_algorithm]
)

st.write(
    f"선택한 알고리즘의 {prediction_year}년 "
    f"{selected_month}월 예측 평균기온은 "
    f"**{prediction:.2f}℃** 입니다."
)


# ==========================================
# 16. 분석 결과 주의사항
# ==========================================
st.divider()

st.subheader("⚠️ 예측 결과를 해석할 때 주의할 점")

st.markdown("""
1. 세 알고리즘은 동일한 실제 CSV 데이터를 사용합니다.
2. 알고리즘마다 학습 방식이 다르므로 예측값도 달라질 수 있습니다.
3. 결정계수는 학습 데이터에 대한 적합도를 나타내며 미래 예측의 정확도를 보장하지 않습니다.
4. 랜덤 포레스트와 그래디언트 부스팅은 학습한 연도 범위 밖에서 기온의 상승·하락 추세를 계속 연장하지 못합니다.
5. 실제 미래 기온은 기후 변화, 기상 조건 등 다양한 요인의 영향을 받습니다.
6. 따라서 결과는 실제 미래 기온이 아닌 통계적 추정값입니다.
""")

st.caption(
    "🌡️ 월별 평균기온 분석 | Linear Regression · Random Forest · Gradient Boosting"
)
