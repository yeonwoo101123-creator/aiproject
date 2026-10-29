
import streamlit as st

st.set_page_config(
    page_title="MBTI 진로 탐험소 🔎",
    page_icon="🧭",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f5f3ff 0%, #f0f9ff 100%);
}
.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(135deg, #7867e8, #49a8d8);
    color: white;
    padding: 30px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 20px;
}
.hero h1 { color: white; }
.career-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e4e2fa;
    margin-bottom: 12px;
}
.tip {
    background: #fff7df;
    padding: 16px;
    border-radius: 14px;
}
.small-note {
    color: #666;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

CAREERS = {
    "ISTJ": {
        "name": "꼼꼼한 현실주의자",
        "emoji": "📋",
        "intro": "계획을 세우고 책임감 있게 일을 마무리하는 강점이 있어!",
        "jobs": [
            {
                "title": "회계사",
                "emoji": "🧮",
                "majors": "회계학과, 경영학과, 경제학과",
                "personality": "꼼꼼함, 정직함, 논리적 사고, 높은 책임감",
                "salary": "약 5,000만~8,000만 원",
                "description": "기업의 재무 정보를 확인하고 회계·세무 업무를 전문적으로 수행해.",
                "skills": "회계 지식, 숫자 분석, 관련 자격시험 준비"
            },
            {
                "title": "품질관리 전문가",
                "emoji": "🔍",
                "majors": "산업공학과, 화학공학과, 기계공학과",
                "personality": "세심함, 분석력, 규칙 준수, 문제 해결 능력",
                "salary": "약 3,500만~5,500만 원",
                "description": "제품이나 서비스가 정해진 기준을 충족하는지 확인하고 개선해.",
                "skills": "데이터 분석, 검사 기준 이해, 문서 작성"
            }
        ]
    },
    "ISFJ": {
        "name": "따뜻한 수호자",
        "emoji": "🫶",
        "intro": "주변을 세심하게 살피고 다른 사람을 돕는 데 강점이 있어!",
        "jobs": [
            {
                "title": "간호사",
                "emoji": "🩺",
                "majors": "간호학과",
                "personality": "공감 능력, 책임감, 세심함, 협력적인 태도",
                "salary": "약 3,500만~5,500만 원",
                "description": "환자의 건강 상태를 살피고 치료와 회복 과정을 도와.",
                "skills": "의학 지식, 의사소통, 간호사 국가시험 준비"
            },
            {
                "title": "초등학교 교사",
                "emoji": "🍎",
                "majors": "교육대학교 초등교육과",
                "personality": "인내심, 배려, 책임감, 설명하는 능력",
                "salary": "약 3,500만~6,000만 원",
                "description": "초등학생에게 여러 교과를 가르치고 학교생활과 성장을 도와.",
                "skills": "교과 지식, 수업 설계, 교원 자격 취득"
            }
        ]
    },
    "INFJ": {
        "name": "통찰력 있는 조언자",
        "emoji": "🌙",
        "intro": "사람의 마음과 사회의 변화를 깊이 생각하는 편이라면 주목!",
        "jobs": [
            {
                "title": "상담심리 전문가",
                "emoji": "💬",
                "majors": "심리학과, 상담학과, 교육학과",
                "personality": "경청, 공감, 윤리 의식, 차분한 판단",
                "salary": "약 3,000만~4,500만 원",
                "description": "사람들이 감정과 고민을 이해하고 문제 해결 방법을 찾도록 도와.",
                "skills": "상담 이론, 면담 기술, 관련 대학원 및 자격 요건 확인"
            },
            {
                "title": "작가·콘텐츠 기획자",
                "emoji": "✍️",
                "majors": "국어국문학과, 문예창작학과, 미디어학과",
                "personality": "창의성, 관찰력, 표현력, 깊이 있는 사고",
                "salary": "약 3,000만~5,000만 원",
                "description": "사람들에게 의미 있는 이야기를 글이나 콘텐츠로 전달해.",
                "skills": "글쓰기, 자료 조사, 스토리 구성"
            }
        ]
    },
    "INTJ": {
        "name": "전략적인 설계자",
        "emoji": "♟️",
        "intro": "복잡한 문제를 분석하고 더 나은 방법을 찾는 걸 좋아한다면!",
        "jobs": [
            {
                "title": "소프트웨어 개발자",
                "emoji": "💻",
                "majors": "컴퓨터공학과, 소프트웨어학과, 인공지능학과",
                "personality": "논리력, 집중력, 독립적인 문제 해결",
                "salary": "약 4,000만~7,000만 원",
                "description": "앱이나 웹사이트, 다양한 소프트웨어를 설계하고 개발해.",
                "skills": "프로그래밍, 알고리즘, 협업과 디버깅"
            },
            {
                "title": "데이터 분석가",
                "emoji": "📊",
                "majors": "통계학과, 산업공학과, 데이터사이언스학과",
                "personality": "분석력, 호기심, 체계적인 사고",
                "salary": "약 3,800만~6,500만 원",
                "description": "데이터에서 패턴을 찾아 기업이나 조직의 의사결정을 도와.",
                "skills": "통계, SQL, 데이터 시각화"
            }
        ]
    },
    "ISTP": {
        "name": "실용적인 탐험가",
        "emoji": "🛠️",
        "intro": "직접 실험하고 도구를 다루며 문제를 해결하는 활동에 도전해 봐!",
        "jobs": [
            {
                "title": "기계공학 엔지니어",
                "emoji": "⚙️",
                "majors": "기계공학과, 메카트로닉스공학과",
                "personality": "실용성, 분석력, 침착함, 관찰력",
                "salary": "약 3,800만~6,000만 원",
                "description": "기계와 장비를 설계하고 작동 원리를 개선해.",
                "skills": "수학·물리, CAD, 설계와 실험"
            },
            {
                "title": "자동차 정비 전문가",
                "emoji": "🚗",
                "majors": "자동차공학과, 미래자동차학과",
                "personality": "꼼꼼함, 기계에 대한 관심, 문제 해결력",
                "salary": "약 3,000만~4,500만 원",
                "description": "자동차의 상태를 점검하고 고장 원인을 찾아 정비해.",
                "skills": "자동차 구조, 진단 장비 활용, 관련 자격증"
            }
        ]
    },
    "ISFP": {
        "name": "감각적인 예술가",
        "emoji": "🎨",
        "intro": "감각과 취향을 살려 무언가를 직접 만들 때 즐거움을 느낀다면!",
        "jobs": [
            {
                "title": "시각 디자이너",
                "emoji": "🖌️",
                "majors": "시각디자인학과, 커뮤니케이션디자인학과",
                "personality": "미적 감각, 관찰력, 창의성, 섬세함",
                "salary": "약 3,000만~4,500만 원",
                "description": "브랜드와 제품, 광고 등에 필요한 시각적 이미지를 만들어.",
                "skills": "디자인 도구, 색채 감각, 포트폴리오 제작"
            },
            {
                "title": "영상 편집자",
                "emoji": "🎬",
                "majors": "영상학과, 영화영상학과, 미디어학과",
                "personality": "감각, 집중력, 스토리 구성, 세부 관찰",
                "salary": "약 3,000만~4,500만 원",
                "description": "영상의 장면과 소리를 편집해 몰입감 있는 콘텐츠를 완성해.",
                "skills": "영상 편집, 촬영 기초, 저작권 이해"
            }
        ]
    },
    "INFP": {
        "name": "상상력 풍부한 중재자",
        "emoji": "🦋",
        "intro": "자신만의 가치관과 상상력을 표현할 수 있는 일을 살펴보자!",
        "jobs": [
            {
                "title": "콘텐츠 작가",
                "emoji": "📖",
                "majors": "문예창작학과, 국어국문학과, 미디어학과",
                "personality": "상상력, 공감, 표현력, 호기심",
                "salary": "약 2,800만~4,500만 원",
                "description": "웹 콘텐츠, 영상 대본, 이야기 등 다양한 글을 기획하고 써.",
                "skills": "글쓰기, 자료 조사, 독자 이해"
            },
            {
                "title": "일러스트레이터",
                "emoji": "🖍️",
                "majors": "회화과, 일러스트레이션 관련 학과, 시각디자인학과",
                "personality": "창의성, 섬세함, 자기표현, 관찰력",
                "salary": "약 2,800만~4,500만 원",
                "description": "책, 광고, 게임 등에 들어가는 그림과 시각 자료를 제작해.",
                "skills": "드로잉, 디지털 작업, 포트폴리오"
            }
        ]
    },
    "INTP": {
        "name": "호기심 많은 사색가",
        "emoji": "🧠",
        "intro": "왜 그런지 탐구하고 새로운 아이디어를 떠올리는 걸 좋아한다면!",
        "jobs": [
            {
                "title": "연구원",
                "emoji": "🔬",
                "majors": "자연과학·공학 계열 관련 학과",
                "personality": "호기심, 논리력, 끈기, 탐구심",
                "salary": "약 3,500만~6,000만 원",
                "description": "특정 분야의 질문을 실험과 분석으로 탐구하고 새로운 지식을 만들어.",
                "skills": "전공 지식, 실험·분석, 연구 보고서 작성"
            },
            {
                "title": "AI·머신러닝 엔지니어",
                "emoji": "🤖",
                "majors": "컴퓨터공학과, 인공지능학과, 수학과",
                "personality": "논리적 사고, 호기심, 실험 정신",
                "salary": "약 4,500만~8,000만 원",
                "description": "데이터를 활용해 예측하거나 학습하는 인공지능 시스템을 개발해.",
                "skills": "Python, 수학·통계, 머신러닝 기초"
            }
        ]
    },
    "ESTP": {
        "name": "에너지 넘치는 도전자",
        "emoji": "⚡",
        "intro": "빠르게 상황을 파악하고 사람들과 부딪치며 배우는 걸 즐긴다면!",
        "jobs": [
            {
                "title": "영업 전문가",
                "emoji": "🤝",
                "majors": "경영학과, 마케팅학과, 유통학과",
                "personality": "적극성, 순발력, 설득력, 대인관계 능력",
                "salary": "약 3,000만~5,000만 원",
                "description": "고객의 필요를 파악하고 제품이나 서비스의 가치를 전달해.",
                "skills": "소통, 협상, 상품 이해"
            },
            {
                "title": "스포츠 지도자",
                "emoji": "🏃",
                "majors": "체육학과, 스포츠과학과, 스포츠지도학과",
                "personality": "활동성, 리더십, 동기 부여, 책임감",
                "salary": "약 2,800만~4,500만 원",
                "description": "사람들이 안전하고 효과적으로 운동하도록 지도해.",
                "skills": "운동 지식, 지도법, 관련 자격 요건 확인"
            }
        ]
    },
    "ESFP": {
        "name": "분위기 메이커",
        "emoji": "🎉",
        "intro": "사람들과 소통하고 현장 분위기를 살리는 활동을 좋아한다면!",
        "jobs": [
            {
                "title": "이벤트 기획자",
                "emoji": "🎪",
                "majors": "광고홍보학과, 문화콘텐츠학과, 이벤트 관련 학과",
                "personality": "친화력, 창의성, 순발력, 협업 능력",
                "salary": "약 3,000만~4,500만 원",
                "description": "축제, 행사, 체험 프로그램을 기획하고 현장을 운영해.",
                "skills": "기획서 작성, 일정 관리, 현장 대응"
            },
            {
                "title": "방송·영상 콘텐츠 제작자",
                "emoji": "📹",
                "majors": "방송영상학과, 미디어학과, 콘텐츠 관련 학과",
                "personality": "표현력, 관찰력, 소통 능력, 순발력",
                "salary": "약 3,000만~5,000만 원",
                "description": "사람들의 관심을 끄는 방송과 디지털 콘텐츠를 기획하거나 제작해.",
                "skills": "기획, 촬영·편집 기초, 저작권 이해"
            }
        ]
    },
    "ENFP": {
        "name": "열정적인 아이디어 뱅크",
        "emoji": "🌈",
        "intro": "새로운 아이디어와 사람들과의 협업에서 에너지를 얻는다면!",
        "jobs": [
            {
                "title": "브랜드 마케터",
                "emoji": "📣",
                "majors": "경영학과, 광고홍보학과, 마케팅학과",
                "personality": "창의성, 소통 능력, 호기심, 유연함",
                "salary": "약 3,500만~5,500만 원",
                "description": "브랜드의 매력을 찾아 고객에게 효과적으로 알리는 전략을 세워.",
                "skills": "시장 조사, 콘텐츠 기획, 데이터 해석"
            },
            {
                "title": "UX/UI 디자이너",
                "emoji": "📱",
                "majors": "디자인학과, 산업디자인학과, HCI 관련 학과",
                "personality": "공감, 창의성, 관찰력, 협업 능력",
                "salary": "약 3,500만~6,000만 원",
                "description": "앱이나 웹사이트를 사람들이 편리하게 사용할 수 있도록 설계해.",
                "skills": "사용자 조사, 화면 설계, 프로토타이핑"
            }
        ]
    },
    "ENTP": {
        "name": "재치 있는 발명가",
        "emoji": "💡",
        "intro": "익숙한 방식에 질문을 던지고 색다른 해결책을 찾는다면!",
        "jobs": [
            {
                "title": "창업가",
                "emoji": "🚀",
                "majors": "경영학과, 산업공학과, 관심 분야의 전공",
                "personality": "도전 정신, 아이디어, 문제 해결력, 유연함",
                "salary": "개인별 편차가 매우 커서 평균을 단정하기 어려움",
                "description": "새로운 제품이나 서비스를 기획하고 사업으로 발전시켜.",
                "skills": "시장 조사, 사업 기획, 재무 기초, 실행력"
            },
            {
                "title": "광고 기획자",
                "emoji": "🧠",
                "majors": "광고홍보학과, 미디어학과, 경영학과",
                "personality": "발상력, 설득력, 분석력, 협업 능력",
                "salary": "약 3,300만~5,500만 원",
                "description": "사람들의 관심을 끌고 브랜드의 목표를 달성할 광고를 기획해.",
                "skills": "아이디어 발상, 소비자 분석, 기획서 작성"
            }
        ]
    },
    "ESTJ": {
        "name": "든든한 관리자",
        "emoji": "📌",
        "intro": "목표와 역할을 정리하고 팀을 체계적으로 이끄는 데 강점이 있어!",
        "jobs": [
            {
                "title": "프로젝트 매니저",
                "emoji": "🗂️",
                "majors": "경영학과, 산업공학과, 정보시스템학과",
                "personality": "조직력, 책임감, 의사결정 능력, 소통",
                "salary": "약 4,000만~7,000만 원",
                "description": "프로젝트의 일정과 예산, 팀의 협업을 관리해 목표 달성을 도와.",
                "skills": "일정 관리, 문서화, 위험 관리, 협업"
            },
            {
                "title": "물류관리 전문가",
                "emoji": "📦",
                "majors": "물류학과, 산업공학과, 경영학과",
                "personality": "계획성, 정확성, 책임감, 판단력",
                "salary": "약 3,500만~5,500만 원",
                "description": "상품이 필요한 곳에 효율적으로 도착하도록 물류 과정을 관리해.",
                "skills": "재고 관리, 데이터 분석, 공급망 이해"
            }
        ]
    },
    "ESFJ": {
        "name": "다정한 협력가",
        "emoji": "💗",
        "intro": "사람들과 협력하고 모두가 잘 어울릴 수 있도록 돕는 걸 좋아한다면!",
        "jobs": [
            {
                "title": "인사 담당자",
                "emoji": "👥",
                "majors": "경영학과, 심리학과, 행정학과",
                "personality": "소통 능력, 공정함, 배려, 조직력",
                "salary": "약 3,500만~5,500만 원",
                "description": "채용, 교육, 인사 제도 등을 통해 조직과 구성원의 성장을 도와.",
                "skills": "문서 작성, 면담, 노동 관련 기초 지식"
            },
            {
                "title": "사회복지사",
                "emoji": "🌱",
                "majors": "사회복지학과",
                "personality": "공감, 책임감, 협력, 존중하는 태도",
                "salary": "약 2,800만~4,000만 원",
                "description": "도움이 필요한 사람과 가족이 필요한 복지 서비스를 이용하도록 지원해.",
                "skills": "사례 관리, 상담 기초, 관련 자격 요건 확인"
            }
        ]
    },
    "ENFJ": {
        "name": "사람을 이끄는 멘토",
        "emoji": "🌟",
        "intro": "다른 사람의 가능성을 발견하고 함께 성장하는 일을 살펴보자!",
        "jobs": [
            {
                "title": "진로·교육 프로그램 기획자",
                "emoji": "🎓",
                "majors": "교육학과, 교육공학과, 청소년학과",
                "personality": "공감, 의사소통, 기획력, 동기 부여",
                "salary": "약 3,000만~4,500만 원",
                "description": "학습과 진로 탐색에 도움이 되는 교육 프로그램을 기획하고 운영해.",
                "skills": "교육 설계, 발표, 프로그램 평가"
            },
            {
                "title": "홍보·PR 전문가",
                "emoji": "📢",
                "majors": "광고홍보학과, 미디어학과, 경영학과",
                "personality": "표현력, 대인관계 능력, 공감, 기획력",
                "salary": "약 3,300만~5,500만 원",
                "description": "기업이나 단체의 소식과 가치를 사람들에게 효과적으로 전달해.",
                "skills": "글쓰기, 미디어 대응, 콘텐츠 기획"
            }
        ]
    },
    "ENTJ": {
        "name": "대담한 리더",
        "emoji": "👑",
        "intro": "큰 목표를 세우고 자원을 활용해 결과를 만드는 데 관심이 있다면!",
        "jobs": [
            {
                "title": "경영 컨설턴트",
                "emoji": "📈",
                "majors": "경영학과, 경제학과, 산업공학과",
                "personality": "분석력, 전략적 사고, 설득력, 추진력",
                "salary": "약 4,500만~8,000만 원",
                "description": "기업이 가진 문제를 분석하고 성과를 높일 전략을 제안해.",
                "skills": "자료 분석, 문제 구조화, 발표와 보고서 작성"
            },
            {
                "title": "사업개발 담당자",
                "emoji": "🤝",
                "majors": "경영학과, 경제학과, 국제통상학과",
                "personality": "협상력, 추진력, 전략적 사고, 소통 능력",
                "salary": "약 3,800만~6,500만 원",
                "description": "새로운 사업 기회와 협력 관계를 찾아 회사의 성장을 도와.",
                "skills": "시장 조사, 협상, 사업 기획"
            }
        ]
    },
    "INTJ": {
        "name": "전략적인 설계자",
        "emoji": "♟️",
        "intro": "복잡한 문제를 분석하고 더 나은 방법을 찾는 걸 좋아한다면!",
        "jobs": [
            {
                "title": "소프트웨어 개발자",
                "emoji": "💻",
                "majors": "컴퓨터공학과, 소프트웨어학과, 인공지능학과",
                "personality": "논리력, 집중력, 독립적인 문제 해결",
                "salary": "약 4,000만~7,000만 원",
                "description": "앱이나 웹사이트, 다양한 소프트웨어를 설계하고 개발해.",
                "skills": "프로그래밍, 알고리즘, 협업과 디버깅"
            },
            {
                "title": "데이터 분석가",
                "emoji": "📊",
                "majors": "통계학과, 산업공학과, 데이터사이언스학과",
                "personality": "분석력, 호기심, 체계적인 사고",
                "salary": "약 3,800만~6,500만 원",
                "description": "데이터에서 패턴을 찾아 기업이나 조직의 의사결정을 도와.",
                "skills": "통계, SQL, 데이터 시각화"
            }
        ]
    }
}

# 중복된 유형을 정리하고, 누락된 유형이 있으면 아래 유형 수 검사를 통해 확인할 수 있어.
MBTI_TYPES = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

# 각 유형의 직업 데이터가 빠지지 않도록 안전하게 구성
# 유형 데이터가 없을 때도 앱이 중단되지 않도록 기본 추천을 제공
DEFAULT_CAREERS = {
    "name": "가능성을 탐색하는 탐험가",
    "emoji": "🧭",
    "intro": "관심 분야와 강점을 알아가며 다양한 진로를 탐색해 보자!",
    "jobs": [
        {
            "title": "진로 탐색 전문가",
            "emoji": "🔎",
            "majors": "교육학과, 심리학과",
            "personality": "호기심, 관찰력, 소통 능력",
            "salary": "직무와 경력에 따라 다름",
            "description": "사람들이 자신의 흥미와 강점을 발견하도록 돕는 일을 해.",
            "skills": "경청, 자료 조사, 진로 정보 이해"
        },
        {
            "title": "콘텐츠 기획자",
            "emoji": "💡",
            "majors": "미디어학과, 문화콘텐츠학과",
            "personality": "창의성, 기획력, 협업 능력",
            "salary": "약 3,000만~5,000만 원",
            "description": "사람들에게 유용하고 재미있는 콘텐츠를 기획해.",
            "skills": "아이디어 발상, 글쓰기, 자료 조사"
        }
    ]
}

# 페이지 상단
st.markdown("""
<div class="hero">
    <h1>🧭 MBTI 진로 탐험소</h1>
    <p>나의 성격 유형을 골라 보고, 새로운 미래를 탐험해 보자!</p>
    <p>✨ 나에게 어울릴 수 있는 진로 2가지를 찾아봐!</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "💡 MBTI는 진로를 결정하는 정답지가 아니야! "
    "추천 직업은 탐색을 위한 아이디어이며, 누구나 다양한 분야에서 성장할 수 있어."
)

# 선택 메뉴
st.subheader("🧩 나의 MBTI는?")
selected_mbti = st.selectbox(
    "16가지 유형 중 하나를 선택해 줘!",
    MBTI_TYPES,
    format_func=lambda x: f"{x} — {CAREERS.get(x, DEFAULT_CAREERS)['name']}"
)

profile = CAREERS.get(selected_mbti, DEFAULT_CAREERS)

st.markdown("---")
st.markdown(
    f"## {profile['emoji']} {selected_mbti} | {profile['name']}"
)
st.write(profile["intro"])
st.write("🎯 아래 두 가지 진로는 네가 더 알아보면 좋을 만한 선택지야.")

# 직업 카드 2개
left, right = st.columns(2)

for column, job in zip((left, right), profile["jobs"]):
    with column:
        st.markdown('<div class="career-card">', unsafe_allow_html=True)
        st.subheader(f"{job['emoji']} {job['title']}")
        st.write(job["description"])

        st.markdown("**🎓 관련 학과**")
        st.write(job["majors"])

        st.markdown("**💡 어울리는 성격·강점**")
        st.write(job["personality"])

        st.markdown("**🛠️ 준비하면 좋은 역량**")
        st.write(job["skills"])

        st.markdown("**💰 참고 연봉**")
        st.write(job["salary"])
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🔎 진로 탐험 미션")

interest = st.selectbox(
    "추가로 관심 있는 분야를 골라 봐!",
    [
        "아직 잘 모르겠어",
        "사람을 돕는 일",
        "과학·기술·컴퓨터",
        "예술·디자인·콘텐츠",
        "경영·경제·창업",
        "교육·상담",
        "스포츠·야외 활동"
    ]
)

if st.button("✨ 나의 탐험 기록 확인하기", use_container_width=True):
    st.success(f"좋아! 네 관심 분야는 '{interest}'이구나.")
    st.write(
        "📌 추천된 직업의 실제 업무를 조사하고, "
        "관련 학과의 교육과정도 비교해 봐. "
        "관심 분야와 잘 맞는지 직접 알아보는 게 가장 중요해!"
    )

st.markdown("---")
st.markdown("""
<div class="tip">
    🌱 <b>진로 탐험 꿀팁!</b><br>
    MBTI가 같아도 좋아하는 과목, 가치관, 경험은 모두 달라.
    추천 결과를 참고하되, 네가 재미있어하는 활동과 잘하는 일도 함께 살펴봐!
</div>
""", unsafe_allow_html=True)

st.caption(
    "※ 연봉은 한국의 직업별 보수를 참고하기 위한 대략적인 예시 범위이며 "
    "공식 통계의 확정 평균값이 아닙니다. 실제 보수는 경력, 업종, 지역, "
    "고용 형태 및 성과 등에 따라 달라질 수 있습니다. "
    "창업가처럼 개인차가 큰 직업은 평균 연봉을 단정하기 어렵습니다."
)
