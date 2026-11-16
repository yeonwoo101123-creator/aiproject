
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
    page_title="아이리스 AI 품종 비교",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 AI 품종 예측 비교")
st.write(
    "3가지 머신러닝 알고리즘이 예측한 "
    "붓꽃 품종을 한눈에 비교해 보세요!"
)

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

possible_paths = [
    BASE_DIR / "Iris(1).csv",
    BASE_DIR / "Iris.csv"
]

CSV_PATH = next(
    (p for p in possible_paths if p.exists()),
    None
)

if CSV_PATH is None:
    st.error("CSV 파일을 상위 폴더에 넣어 주세요.")
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

if df["품종"].value_counts().min() < 5:
    st.error("각 품종에 최소 5개 이상의 데이터가 필요합니다.")
    st.stop()


# ==========================================
# 4. 사용할 속성
# ==========================================

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
# 5. 품종 이름과 색상
# ==========================================

species_names = {
    "Iris-setosa": "🌼 Setosa",
    "Iris-versicolor": "🌺 Versicolor",
    "Iris-virginica": "🌸 Virginica"
}

colors = {
    "Iris-setosa": "#FFB6C1",
    "Iris-versicolor": "#87CEEB",
    "Iris-virginica": "#98D8A5"
}


# ==========================================
# 6. 알고리즘 설명
# ==========================================

algorithm_info = {

    "KNN": {
        "title": "① KNN (K-최근접 이웃)",
        "description": """
**작동 원리**

1. 기존 붓꽃 데이터의 위치를 확인합니다.
2. 입력한 꽃과 가장 가까운 데이터 5개를 찾습니다.
3. 5개 중 가장 많이 등장한 품종으로 예측합니다.

**핵심:** 주변 데이터의 다수결로 품종을 결정합니다.

**특징:** 이해하기 쉽고 데이터 간 거리를 활용합니다.
"""
    },

    "SVM": {
        "title": "② SVM (서포트 벡터 머신)",
        "description": """
**작동 원리**

1. 서로 다른 품종의 데이터를 구분합니다.
2. 품종 사이의 결정 경계를 찾습니다.
3. 새로운 데이터가 어느 영역에 속하는지 판단합니다.

**핵심:** 데이터를 구분하는 최적의 경계를 찾습니다.

**특징:** 복잡한 분류 문제에도 활용할 수 있습니다.
"""
    },

    "Random Forest": {
        "title": "③ 랜덤 포레스트",
        "description": """
**작동 원리**

1. 여러 개의 결정 트리를 만듭니다.
2. 각 결정 트리가 독립적으로 품종을 예측합니다.
3. 여러 트리의 예측 결과를 종합합니다.
4. 다수결을 통해 최종 품종을 결정합니다.

**핵심:** 여러 결정 트리의 예측을 결합합니다.

**특징:** 여러 모델의 결과를 종합하는 앙상블 알고리즘입니다.
"""
    }
}


# ==========================================
# 7. 세 가지 모델 생성 함수
# ==========================================

def create_models():

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

    return models


# ==========================================
# 8. 예측 및 비교 함수
# ==========================================

def run_prediction(
    feature_columns,
    x_label,
    y_label,
    tab_key
):

    st.subheader("✏️ 꽃의 크기 입력하기")

    x_min = float(df[feature_columns[0]].min())
    x_max = float(df[feature_columns[0]].max())

    y_min = float(df[feature_columns[1]].min())
    y_max = float(df[feature_columns[1]].max())

    st.info(
        f"""
**입력 가능한 값의 범위**

- {x_label}: {x_min} ~ {x_max} cm
- {y_label}: {y_min} ~ {y_max} cm

※ CSV 데이터에서 측정된 실제 최솟값과 최댓값입니다.
"""
    )

    col1, col2 = st.columns(2)

    with col1:
        x_value = st.number_input(
            x_label + " (cm)",
            min_value=x_min,
            max_value=x_max,
            value=round(
                float(df[feature_columns[0]].mean()), 1
            ),
            step=0.1,
            key=tab_key + "_x"
        )

    with col2:
        y_value = st.number_input(
            y_label + " (cm)",
            min_value=y_min,
            max_value=y_max,
            value=round(
                float(df[feature_columns[1]].mean()), 1
            ),
            step=0.1,
            key=tab_key + "_y"
        )

    # 입력 데이터
    X = df[feature_columns]

    input_data = pd.DataFrame(
        [[x_value, y_value]],
        columns=feature_columns
    )

    # ======================================
    # 9. 세 알고리즘 동시에 학습 및 예측
    # ======================================

    models = create_models()

    results = []
    probability_data = []

    for name, model in models.items():

        # 모델 학습
        model.fit(X, y)

        # 품종 예측
        prediction = model.predict(input_data)[0]

        # 품종별 확률
        probabilities = model.predict_proba(input_data)[0]

        # 예측한 품종의 확률
        predicted_index = list(
            model.classes_
        ).index(prediction)

        confidence = probabilities[predicted_index]

        results.append({
            "알고리즘": name,
            "예측 품종": species_names.get(
                prediction, prediction
            ),
            "예측 확률": confidence * 100,
            "원래 품종": prediction
        })

        probability_row = {
            "알고리즘": name
        }

        for species, probability in zip(
            model.classes_,
            probabilities
        ):
            probability_row[
                species_names.get(species, species)
            ] = round(probability * 100, 1)

        probability_data.append(probability_row)

    result_df = pd.DataFrame(results)

    # ======================================
    # 10. 알고리즘별 예측 결과 비교
    # ======================================

    st.divider()

    st.header("🔮 3가지 알고리즘 예측 결과")

    st.write(
        "동일한 입력값을 이용해 세 알고리즘이 "
        "각각 예측한 결과입니다."
    )

    # 세 개의 결과 카드
    card_cols = st.columns(3)

    for i, result in enumerate(results):

        with card_cols[i]:

            st.markdown(
                f"### {result['알고리즘']}"
            )

            st.metric(
                "예측 품종",
                result["원래 품종"].replace("Iris-", "")
            )

            st.metric(
                "예측 확률",
                f"{result['예측 확률']:.1f}%"
            )

    # 결과 비교 표
    st.subheader("📋 알고리즘별 결과 비교")

    comparison_table = pd.DataFrame({
        "알고리즘": [
            r["알고리즘"] for r in results
        ],
        "예측 품종": [
            r["예측 품종"] for r in results
        ],
        "예측 확률": [
            f"{r['예측 확률']:.1f}%"
            for r in results
        ]
    })

    st.dataframe(
        comparison_table,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 11. 예측 결과 일치 여부
    # ======================================

    predictions = [
        r["원래 품종"] for r in results
    ]

    if len(set(predictions)) == 1:

        st.success(
            "🎉 세 가지 알고리즘이 모두 같은 품종을 예측했습니다!"
        )

        st.write(
            "세 알고리즘의 예측 결과가 일치합니다: "
            + species_names.get(predictions[0], predictions[0])
        )

    else:

        st.warning(
            "⚠️ 알고리즘에 따라 예측 결과가 다릅니다."
        )

        st.write(
            "서로 다른 알고리즘이 입력 데이터를 "
            "다르게 분류했습니다. 각 결과를 비교해 보세요."
        )

    # ======================================
    # 12. 품종별 예측 확률 비교
    # ======================================

    st.subheader("📊 품종별 예측 확률 비교")

    probability_df = pd.DataFrame(probability_data)

    st.dataframe(
        probability_df,
        use_container_width=True,
        hide_index=True
    )

    # 확률 비교 그래프
    probability_plot = probability_df.set_index(
        "알고리즘"
    )

    fig_probability = go.Figure()

    for species in probability_plot.columns:

        fig_probability.add_trace(
            go.Bar(
                name=species,
                x=probability_plot.index,
                y=probability_plot[species],
                text=[
                    f"{v:.1f}%"
                    for v in probability_plot[species]
                ],
                textposition="auto"
            )
        )

    fig_probability.update_layout(
        title="알고리즘별 품종 예측 확률",
        xaxis_title="분류 알고리즘",
        yaxis_title="예측 확률 (%)",
        barmode="group",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        height=400
    )

    st.plotly_chart(
        fig_probability,
        use_container_width=True,
        key=tab_key + "_probability"
    )

    # ======================================
    # 13. 기존 데이터와 입력값 그래프
    # ======================================

    st.divider()

    st.subheader("🌸 붓꽃 데이터 시각화")

    fig = go.Figure()

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
                )
            )
        )

    # 사용자 입력값
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
        legend_title="붓꽃 품종"
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
        key=tab_key + "_scatter"
    )

    # ======================================
    # 14. 알고리즘 작동 원리
    # ======================================

    st.divider()

    st.header("📚 알고리즘 3개의 작동 원리")

    for name, info in algorithm_info.items():

        with st.expander(
            info["title"],
            expanded=True
        ):

            st.markdown(
                info["description"]
            )

    # ======================================
    # 15. 입력값 정리
    # ======================================

    st.divider()

    st.subheader("📝 입력한 데이터")

    input_result = pd.DataFrame({
        "측정 항목": [
            x_label,
            y_label
        ],
        "입력값": [
            f"{x_value:.1f} cm",
            f"{y_value:.1f} cm"
        ]
    })

    st.dataframe(
        input_result,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "※ 예측 확률은 각 모델의 추정값이며 "
        "실제 예측 정확도와는 다릅니다."
    )


# ==========================================
# 16. 탭 구성
# ==========================================

tab1, tab2 = st.tabs([
    "🌷 꽃잎으로 품종 예측",
    "🍃 꽃받침으로 품종 예측"
])


# ==========================================
# 17. 꽃잎 예측 탭
# ==========================================

with tab1:

    st.header("🌷 꽃잎 크기로 품종 예측")

    st.write(
        "꽃잎 길이와 꽃잎 너비를 입력하세요. "
        "세 가지 알고리즘이 동시에 예측합니다."
    )

    run_prediction(
        feature_columns=petal_features,
        x_label="꽃잎 길이",
        y_label="꽃잎 너비",
        tab_key="petal"
    )


# ==========================================
# 18. 꽃받침 예측 탭
# ==========================================

with tab2:

    st.header("🍃 꽃받침 크기로 품종 예측")

    st.write(
        "꽃받침 길이와 꽃받침 너비를 입력하세요. "
        "세 가지 알고리즘이 동시에 예측합니다."
    )

    run_prediction(
        feature_columns=sepal_features,
        x_label="꽃받침 길이",
        y_label="꽃받침 너비",
        tab_key="sepal"
    )


# ==========================================
# 19. 마무리
# ==========================================

st.divider()

st.markdown("""
### 💡 데이터 과학 탐구 활동

1. 같은 입력값에서 세 알고리즘의 예측 품종은 같을까요?
2. 세 알고리즘 중 예측 확률이 가장 높은 것은 무엇일까요?
3. 꽃잎과 꽃받침 중 어떤 속성이 품종을 구분하기 좋을까요?
4. 알고리즘을 바꾸면 예측 결과는 어떻게 달라질까요?

**직접 입력값을 바꾸면서 결과를 비교해 보세요! 🌱**
""")

st.caption(
    "아이리스 데이터 기반 3가지 머신러닝 분류 알고리즘 비교 프로그램"
)
