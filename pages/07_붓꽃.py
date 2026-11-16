
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="아이리스 AI 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 AI 품종 예측")
st.write(
    "꽃잎 또는 꽃받침의 크기를 입력하고 "
    "3가지 머신러닝 알고리즘으로 품종을 예측해 보세요!"
)

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# CSV 파일명 자동 확인
possible_paths = [
    BASE_DIR / "Iris(1).csv",
    BASE_DIR / "Iris.csv"
]

CSV_PATH = next(
    (p for p in possible_paths if p.exists()),
    None
)

if CSV_PATH is None:
    st.error(
        "Iris(1).csv 또는 Iris.csv 파일을 "
        "프로젝트 상위 폴더에 넣어 주세요."
    )
    st.stop()

try:
    try:
        df = pd.read_csv(CSV_PATH, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()


# ==========================================
# 3. 데이터 전처리
# ==========================================

required_columns = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

df = df[required_columns].copy()

for col in required_columns[:4]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

if df["품종"].nunique() != 3:
    st.error("세 가지 품종 데이터가 필요합니다.")
    st.stop()

if len(df) < 5 or df["품종"].value_counts().min() < 5:
    st.error("각 품종에 최소 5개 이상의 데이터가 필요합니다.")
    st.stop()

# 학습에 사용할 속성
petal_features = [
    "꽃잎 길이",
    "꽃잎 너비"
]

sepal_features = [
    "꽃받침 길이",
    "꽃받침 너비"
]

y = df["품종"]


# ==========================================
# 4. 머신러닝 알고리즘 3개 만들기
# ==========================================

models = {

    "KNN": Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsClassifier(
            n_neighbors=5
        ))
    ]),

    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC(
            kernel="rbf",
            C=1.0,
            probability=True,
            random_state=42
        ))
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
}


# ==========================================
# 5. 알고리즘 작동 원리
# ==========================================

algorithm_info = {

    "KNN": {
        "title": "① KNN (K-최근접 이웃)",
        "description": """
        **작동 원리**

        1. 기존 붓꽃 데이터의 위치를 확인합니다.
        2. 사용자가 입력한 꽃과 가까운 데이터 5개를 찾습니다.
        3. 가장 많이 등장한 품종을 선택합니다.

        **핵심 개념:** 주변 이웃의 다수결로 품종을 결정합니다.

        **특징:** 원리를 이해하기 쉽고 데이터의 거리와
        주변 분포를 이용하는 분류 알고리즘입니다.
        """
    },

    "SVM": {
        "title": "② SVM (서포트 벡터 머신)",
        "description": """
        **작동 원리**

        1. 서로 다른 품종의 데이터를 구분합니다.
        2. 품종 사이를 나누는 결정 경계를 찾습니다.
        3. 새로운 데이터가 경계의 어느 쪽에 위치하는지
           판단하여 품종을 예측합니다.

        **핵심 개념:** 품종을 구분하는 최적의 경계를 찾습니다.

        **특징:** 복잡한 데이터의 분류에도 활용할 수 있습니다.
        이번 프로그램에서는 RBF 커널을 사용합니다.
        """
    },

    "Random Forest": {
        "title": "③ 랜덤 포레스트 (Random Forest)",
        "description": """
        **작동 원리**

        1. 여러 개의 결정 트리를 만듭니다.
        2. 각 결정 트리가 입력 데이터를 분석합니다.
        3. 여러 트리의 예측 결과를 모읍니다.
        4. 다수의 트리가 선택한 품종을 예측합니다.

        **핵심 개념:** 여러 결정 트리의 예측을 결합합니다.

        **특징:** 여러 트리를 활용하는 앙상블 분류 알고리즘입니다.
        """
    }
}


# ==========================================
# 6. 품종 이름
# ==========================================

species_names = {
    "Iris-setosa": "🌼 아이리스 세토사 (Setosa)",
    "Iris-versicolor": "🌺 아이리스 버시컬러 (Versicolor)",
    "Iris-virginica": "🌸 아이리스 버지니카 (Virginica)"
}

colors = {
    "Iris-setosa": "#FFB6C1",
    "Iris-versicolor": "#87CEEB",
    "Iris-virginica": "#98D8A5"
}


# ==========================================
# 7. 예측 및 그래프 함수
# ==========================================

def run_prediction(
    feature_columns,
    x_label,
    y_label,
    tab_key
):

    st.subheader("✏️ 측정값 입력하기")

    # 입력 가능한 최소/최대 범위
    x_min = float(df[feature_columns[0]].min())
    x_max = float(df[feature_columns[0]].max())

    y_min = float(df[feature_columns[1]].min())
    y_max = float(df[feature_columns[1]].max())

    st.info(
        f"""
        **입력 가능한 값의 범위**

        - {x_label}: {x_min} ~ {x_max} cm
        - {y_label}: {y_min} ~ {y_max} cm

        ※ 제공된 CSV 데이터의 실제 최솟값과 최댓값입니다.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        x_value = st.number_input(
            x_label + " (cm)",
            min_value=x_min,
            max_value=x_max,
            value=float(df[feature_columns[0]].mean()),
            step=0.1,
            format="%.1f",
            key=tab_key + "_x"
        )

    with col2:
        y_value = st.number_input(
            y_label + " (cm)",
            min_value=y_min,
            max_value=y_max,
            value=float(df[feature_columns[1]].mean()),
            step=0.1,
            format="%.1f",
            key=tab_key + "_y"
        )

    st.divider()

    # 알고리즘 선택
    st.subheader("🤖 분류 알고리즘 선택")

    selected_algorithm = st.selectbox(
        "사용할 머신러닝 알고리즘",
        list(models.keys()),
        key=tab_key + "_model"
    )

    # 선택한 속성만 학습
    X = df[feature_columns]

    model = models[selected_algorithm]

    model.fit(X, y)

    # 사용자 입력값
    input_data = pd.DataFrame(
        [[x_value, y_value]],
        columns=feature_columns
    )

    # 예측
    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    st.subheader("🔮 AI 예측 결과")

    st.success(
        "예측 품종: "
        + species_names.get(prediction, prediction)
    )

    st.write("### 품종별 예측 확률")

    for species, probability in zip(
        model.classes_,
        probabilities
    ):

        st.write(
            species_names.get(species, species)
        )

        st.progress(float(probability))

        st.caption(
            f"예측 확률: {probability * 100:.1f}%"
        )

    st.divider()

    # ======================================
    # 그래프
    # ======================================

    st.subheader("📊 붓꽃 데이터 시각화")

    fig = go.Figure()

    # 기존 품종 데이터
    for species in df["품종"].unique():

        species_data = df[
            df["품종"] == species
        ]

        fig.add_trace(
            go.Scatter(
                x=species_data[feature_columns[0]],
                y=species_data[feature_columns[1]],
                mode="markers",
                name=species_names.get(species, species),

                marker=dict(
                    size=9,
                    color=colors.get(species, "#AAAAAA"),
                    opacity=0.7
                ),

                hovertemplate=(
                    x_label + ": %{x}<br>"
                    + y_label + ": %{y}<br>"
                    + species + "<extra></extra>"
                )
            )
        )

    # 사용자 입력값: 연보라색 별
    fig.add_trace(
        go.Scatter(
            x=[x_value],
            y=[y_value],
            mode="markers+text",

            name="사용자 입력값",

            text=["★ 내 입력값"],
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

    fig.update_layout(
        title="붓꽃 품종별 크기 비교",
        xaxis_title=x_label + " (cm)",
        yaxis_title=y_label + " (cm)",
        template="plotly_white",
        height=550,
        legend_title="품종",
        hovermode="closest"
    )

    fig.update_xaxes(
        range=[x_min - 0.3, x_max + 0.3]
    )

    fig.update_yaxes(
        range=[y_min - 0.2, y_max + 0.2]
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=tab_key + "_chart"
    )

    # ======================================
    # 알고리즘 설명: 그래프 아래
    # ======================================

    st.divider()

    st.subheader("📚 머신러닝 알고리즘 작동 원리")

    st.write(
        f"현재 선택한 알고리즘: **{selected_algorithm}**"
    )

    # 선택한 알고리즘을 먼저 표시
    selected_info = algorithm_info[selected_algorithm]

    with st.container(border=True):

        st.markdown(
            "### " + selected_info["title"]
        )

        st.markdown(
            selected_info["description"]
        )

    st.write("### 다른 알고리즘도 알아보기")

    for name, info in algorithm_info.items():

        if name != selected_algorithm:

            with st.expander(info["title"]):

                st.markdown(
                    info["description"]
                )

    st.caption(
        "※ 예측 확률은 모델이 계산한 분류별 확률이며 "
        "실제 품종일 가능성을 보장하지는 않습니다."
    )


# ==========================================
# 8. 탭 만들기
# ==========================================

tab1, tab2 = st.tabs([
    "🌷 꽃잎으로 품종 예측",
    "🍃 꽃받침으로 품종 예측"
])


# ==========================================
# 9. 첫 번째 탭: 꽃잎
# ==========================================

with tab1:

    st.header("🌷 꽃잎 크기로 품종 예측")

    st.write(
        "꽃잎의 길이와 너비를 입력하여 "
        "붓꽃 품종을 예측해 보세요."
    )

    run_prediction(
        feature_columns=petal_features,
        x_label="꽃잎 길이",
        y_label="꽃잎 너비",
        tab_key="petal"
    )


# ==========================================
# 10. 두 번째 탭: 꽃받침
# ==========================================

with tab2:

    st.header("🍃 꽃받침 크기로 품종 예측")

    st.write(
        "꽃받침의 길이와 너비를 입력하여 "
        "붓꽃 품종을 예측해 보세요."
    )

    run_prediction(
        feature_columns=sepal_features,
        x_label="꽃받침 길이",
        y_label="꽃받침 너비",
        tab_key="sepal"
    )


# ==========================================
# 11. 마무리
# ==========================================

st.divider()

st.markdown(
    """
    ### 💡 데이터 과학 학습 포인트

    - 같은 데이터라도 사용하는 속성에 따라 예측 결과가 달라질 수 있습니다.
    - 같은 속성을 사용해도 알고리즘에 따라 예측 결과가 달라질 수 있습니다.
    - 꽃잎과 꽃받침 중 어떤 속성이 품종을 더 잘 구분하는지 비교해 보세요.
    """
)

st.caption(
    "아이리스 데이터 150개를 이용한 머신러닝 분류 프로그램"
)
