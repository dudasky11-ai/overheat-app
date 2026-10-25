# 스마트폰 과열 진단 웹앱 (Streamlit)
from datetime import datetime, timedelta, timezone
import streamlit as st

# 한국 시간 (서버는 세계 표준시를 쓰므로 9시간을 더함)
KST = timezone(timedelta(hours=9))


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


# 3. 기록 추가 함수: 진단 한 번의 결과를 딕셔너리로 만들어 기록 리스트에 붙임
def add_record(temp, charge, cover, game, total, level):
    record = {
        "시각": datetime.now(KST).strftime("%H:%M:%S"),
        "온도": temp,
        "충전 방식": charge,
        "케이스": cover,
        "게임": game,
        "점수": total,
        "단계": level,
    }
    st.session_state["history"].append(record)


# 4. CSV 만들기 함수: 기록 리스트를 쉼표로 구분한 글자로 바꿈
def make_csv(history):
    lines = ["시각,온도,충전 방식,케이스,게임,점수,단계"]
    for r in history:
        line = f"{r['시각']},{r['온도']},{r['충전 방식']},{r['케이스']},{r['게임']},{r['점수']},{r['단계']}"
        lines.append(line)
    return "\n".join(lines)


# 5. 기록 리스트 준비: 처음 접속했을 때만 빈 리스트를 만듦
if "history" not in st.session_state:
    st.session_state["history"] = []

# 6. 화면: 제목과 입력 위젯
st.title("📱 스마트폰 과열 진단")
st.write("지금 상황을 고르면 배터리 과열 위험을 알려드려요.")

temp = st.slider("주변 온도 (°C)", -30, 60, 25)
charge = st.radio("충전 방식", ["일반", "고속"], horizontal=True)
cover = st.radio("케이스를 끼웠나요?", ["아니오", "예"], horizontal=True)
game = st.radio("충전하면서 게임 중인가요?", ["아니오", "예"], horizontal=True)

# 7. 진단 버튼을 누르면 계산하고 결과 출력
if st.button("진단하기", type="primary"):
    scores = calc_score(temp, charge, cover, game)
    total = sum(scores.values())
    level, advice = judge(total)
    add_record(temp, charge, cover, game, total, level)

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

# 8. 진단 기록 표와 내려받기, 지우기 버튼
history = st.session_state["history"]
if len(history) > 0:
    st.subheader("진단 기록")
    st.dataframe(history)

    st.download_button(
        "기록 CSV로 내려받기",
        make_csv(history).encode("utf-8-sig"),
        file_name="진단기록.csv",
        mime="text/csv",
    )
    if st.button("기록 지우기"):
        st.session_state["history"] = []
        st.rerun()

# 9. 점수 변화 그래프: 기록이 2개 이상일 때만 그림
if len(history) >= 2:
    st.subheader("점수 변화 그래프")
    chart_data = []
    for i in range(len(history)):
        chart_data.append({"진단 순서": i + 1, "점수": history[i]["점수"]})
    st.line_chart(chart_data, x="진단 순서", y="점수")
    st.caption("7점 이상은 위험, 3점 이상은 주의, 그 아래는 안전입니다.")
