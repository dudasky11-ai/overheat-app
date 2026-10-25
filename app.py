# 스마트폰 과열 진단 웹앱 (Streamlit)
import streamlit as st


# 1. 점수 계산 함수: 조건을 받아서 항목별 점수를 딕셔너리로 돌려줌
def calc_score(temp, charge, cover, game):
    if temp >= 35:
        temp_score = 3
    elif temp >= 30:
        temp_score = 2
    elif temp >= 25:
        temp_score = 1
    else:
        temp_score = 0

    scores = {
        "주변 온도": temp_score,
        "고속충전": 2 if charge == "고속" else 0,
        "케이스": 1 if cover == "예" else 0,
        "충전 중 게임": 3 if game == "예" else 0,
    }
    return scores


# 2. 판정 함수: 총점으로 단계와 행동 요령을 돌려줌
def judge(total):
    if total >= 7:
        return "위험", "충전을 멈추고 케이스를 벗긴 뒤 서늘한 곳에 두세요."
    elif total >= 3:
        return "주의", "게임을 멈추거나 케이스를 벗기세요."
    else:
        return "안전", "정상적으로 사용해도 됩니다."


# 3. 화면: 제목과 입력 위젯
st.title("📱 스마트폰 과열 진단")
st.write("지금 상황을 고르면 배터리 과열 위험을 알려드려요.")

temp = st.slider("주변 온도 (°C)", -30, 60, 25)
charge = st.radio("충전 방식", ["일반", "고속"], horizontal=True)
cover = st.radio("케이스를 끼웠나요?", ["아니오", "예"], horizontal=True)
game = st.radio("충전하면서 게임 중인가요?", ["아니오", "예"], horizontal=True)

# 4. 진단 버튼을 누르면 계산하고 결과 출력
if st.button("진단하기", type="primary"):
    scores = calc_score(temp, charge, cover, game)
    total = sum(scores.values())
    level, advice = judge(total)

    st.subheader(f"위험 점수: {total}점 / 9점")
    st.progress(total / 9)

    if level == "위험":
        st.error(f"🔴 [위험] {advice}")
    elif level == "주의":
        st.warning(f"🟡 [주의] {advice}")
    else:
        st.success(f"🟢 [안전] {advice}")

    # 항목별 점수 표시
    st.write("**항목별 점수**")
    for name, point in scores.items():
        st.write(f"- {name}: {point}점")
