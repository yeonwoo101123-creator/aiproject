
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier


# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="아이리스 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 붓꽃 품종 예측")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "AI가 붓꽃의 품종을 예측해 줍니다!"
)

st.divider()


# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------
# py 파일은 pages 폴더,
# CSV 파일은 상위 폴더에 위치

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "Iris.csv"

if not CSV_PATH.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("Iris(1).csv 파일이 프로젝트의 상위 폴더에 있는지 확인하세요.")
    st.stop()

try:
    try:
        df = pd.read_csv(CSV_PATH, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()


# --------------------------------
# 3. 데이터 확인
# --------------------------------
required_columns = [
    "꽃잎 길이",
    "꽃잎 너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

df = df.dropna(subset=required_columns).copy()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]


# --------------------------------
# 4. 입력 가능한 범위 계산
# --------------------------------
min_length = float(df["꽃잎 길이"].min())
max_length = float(df["꽃잎 길이"].max())

min_width = float(df["꽃잎 너비"].min())
max_width = float(df["꽃잎 너비"].max())


# --------------------------------
# 5. 머신러닝 모델 만들기
# --------------------------------
# 표준화 + KNN 분류 알고리즘

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

# 전체 데이터로 학습
model.fit(X, y)


# --------------------------------
# 6. 모델 설명
# --------------------------------
with st.expander("🤖 AI가 사용하는 알고리즘 알아보기"):
    st.markdown("""
    **KNN (K-최근접 이웃 알고리즘)**

    1. 기존 붓꽃 데이터를 학습합니다.
    2. 사용자가 꽃잎 길이와 너비를 입력합니다.
    3. 입력값과 가까운 데이터 5개를 찾습니다.
    4. 가장 많이 등장한 품종을 예측 결과로 보여줍니다.

    입력값의 크기 차이를 줄이기 위해
    StandardScaler로 데이터를 표준화합니다.
    """)


# --------------------------------
# 7. 사용자 입력
# --------------------------------
st.subheader("✏️ 꽃잎 크기 입력하기")

st.info(
    f"꽃잎 길이: {min_length:.1f} ~ {max_length:.1f}cm\n\n"
    f"꽃잎 너비: {min_width:.1f} ~ {max_width:.1f}cm\n\n"
    "※ 위 범위는 제공된 CSV 데이터의 실제 측정 범위입니다."
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=3.8,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=1.2,
        step=0.1,
        format="%.1f"
    )


# --------------------------------
# 8. 품종 예측
# --------------------------------
input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=["꽃잎 길이", "꽃잎 너비"]
)

prediction = model.predict(input_data)[0]

# 품종별 예측 확률
probabilities = model.predict_proba(input_data)[0]

st.divider()

st.subheader("🔮 AI 품종 예측 결과")

species_names = {
    "Iris-setosa": "🌼 아이리스 세토사 (Setosa)",
    "Iris-versicolor": "🌺 아이리스 버시컬러 (Versicolor)",
    "Iris-virginica": "🌸 아이리스 버지니카 (Virginica)"
}

st.success(
    f"예측된 품종은 {species_names.get(prediction, prediction)} 입니다!"
)

# 예측 확률 표시
st.write("### 품종별 예측 확률")

for species, probability in zip(
    model.classes_, probabilities
):
    st.write(f"**{species_names.get(species, species)}**")
    st.progress(float(probability))
    st.caption(f"{probability * 100:.1f}%")


# --------------------------------
# 9. 그래프 그리기
# --------------------------------
st.divider()

st.subheader("📊 꽃잎 크기 시각화")

st.write(
    "기존 붓꽃 데이터와 사용자가 입력한 위치를 비교해 보세요."
)

fig = go.Figure()

# 기존 품종별 데이터 표시
colors = {
    "Iris-setosa": "#FFB6C1",
    "Iris-versicolor": "#87CEEB",
    "Iris-virginica": "#98D8A5"
}

for species in df["품종"].unique():

    species_data = df[df["품종"] == species]

    fig.add_trace(
        go.Scatter(
            x=species_data["꽃잎 길이"],
            y=species_data["꽃잎 너비"],
            mode="markers",
            name=species_names.get(species, species),
            marker=dict(
                size=9,
                color=colors.get(species, "#AAAAAA"),
                opacity=0.65
            )
        )
    )


# 사용자가 입력한 값: 연보라색 별
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers+text",
        name="내가 입력한 꽃",
        text=["내 입력값 ★"],
        textposition="top center",
        marker=dict(
            symbol="star",
            size=25,
            color="#C8A2C8",
            line=dict(
                color="#8064A2",
                width=2
            )
        )
    )
)


# 그래프 레이아웃
fig.update_layout(
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    title="아이리스 품종별 꽃잎 크기 비교",
    template="plotly_white",
    height=600,
    legend_title="붓꽃 품종",
    hovermode="closest"
)

fig.update_xaxes(
    range=[
        min_length - 0.3,
        max_length + 0.3
    ]
)

fig.update_yaxes(
    range=[
        min_width - 0.2,
        max_width + 0.2
    ]
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------
# 10. 입력값 정리
# --------------------------------
st.subheader("📝 나의 입력 정보")

result_df = pd.DataFrame({
    "항목": [
        "꽃잎 길이",
        "꽃잎 너비",
        "예측 품종"
    ],
    "입력값": [
        f"{petal_length:.1f} cm",
        f"{petal_width:.1f} cm",
        prediction
    ]
})

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------
# 11. 안내
# --------------------------------
st.divider()

st.caption(
    "본 프로그램은 제공된 아이리스 데이터 150개를 "
    "이용하여 KNN 분류 모델을 학습하고 예측합니다."
)

st.caption(
    "예측 결과는 학습 데이터와 알고리즘에 기반한 "
    "추정값이며 실제 품종을 확정하는 것은 아닙니다."
)

