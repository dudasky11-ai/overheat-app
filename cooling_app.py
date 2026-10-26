# 냉각 소재 비교 계산기 웹앱 (Streamlit)
# 음료를 원하는 온도로 식히려면 소재별로 얼마나 필요한지 계산하고,
# 녹는 소재(잠열)와 녹지 않는 소재(현열)의 차이를 비교함
import sys
import streamlit as st
from streamlit import runtime
from streamlit.web import cli

# 0. 파이썬에서 그냥 Run(F5)으로 실행했을 때는 Streamlit을 대신 켜 줌
#    (streamlit run 으로 실행된 경우에는 runtime.exists()가 True라서 건너뜀)
if __name__ == "__main__" and not runtime.exists():
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(cli.main())

WATER_C = 4.18  # 물(음료)의 비열 (J/g·°C)

# 1. 냉각 소재 정보 (콘솔 버전과 같음)
#    c: 고체일 때 비열(J/g·°C), melt: 녹는점(°C, 녹지 않으면 None)
#    latent: 융해열(J/g), c_liquid: 녹은 뒤 비열, piece: 한 개 무게(g), mix: 음료에 섞이는지
MATERIALS = {
    "얼음": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 10, "mix": True},
    "젤 아이스팩": {"c": 2.1, "melt": 0, "latent": 334, "c_liquid": 4.18, "piece": 100, "mix": False},
    "스테인리스 큐브": {"c": 0.50, "melt": None, "latent": 0, "c_liquid": 0, "piece": 25, "mix": False},
    "위스키 스톤(화강암)": {"c": 0.79, "melt": None, "latent": 0, "c_liquid": 0, "piece": 20, "mix": False},
}


# 2. 소재 1g이 처음 온도(start)에서 목표 온도(target)까지 데워지며 흡수하는 열 (콘솔 버전과 같음)
def heat_per_gram(m, start, target):
    if m["melt"] is None or target <= m["melt"]:
        return m["c"] * (target - start)  # 현열만 (녹지 않음)

    solid = m["c"] * (m["melt"] - start)          # 녹는점까지 데워짐 (현열)
    melting = m["latent"]                          # 녹음 (잠열)
    liquid = m["c_liquid"] * (target - m["melt"])  # 녹은 뒤 목표 온도까지 (현열)
    return solid + melting + liquid


# 3. 음료가 목표 온도까지 식으며 내놓는 열 (콘솔 버전과 같음)
def drink_heat(mass, drink_temp, target):
    return mass * WATER_C * (drink_temp - target)


# 4. 입력값 검사: 문제가 있으면 안내 문장, 없으면 None을 돌려줌
def check_input(mass, drink_temp, target, start):
    if mass <= 0:
        return "음료 양은 0보다 커야 해요."
    elif target >= drink_temp:
        return "목표 온도는 음료 온도보다 낮아야 해요."
    elif target <= start:
        return "목표 온도는 냉각 소재 온도보다 높아야 해요. (더 차가운 것으로는 식힐 수 없어요)"
    elif target < 0:
        return "목표 온도가 0°C보다 낮으면 음료가 얼어요."
    return None


# 5. 소재마다 필요한 양을 계산해 표의 행(딕셔너리) 리스트로 돌려줌
def compare(mass, drink_temp, target, start):
    q = drink_heat(mass, drink_temp, target)
    rows = []
    ice_grams = None
    for name in MATERIALS:
        m = MATERIALS[name]
        per_gram = heat_per_gram(m, start, target)
        grams = q / per_gram
        if name == "얼음":
            ice_grams = grams

        if m["mix"]:
            water_ratio = grams / (mass + grams) * 100
            dilution = f"{water_ratio:.0f}% 묽어짐"
        else:
            dilution = "안 묽어짐"

        rows.append({
            "냉각 소재": name,
            "1g당 흡수열 (J)": round(per_gram, 1),
            "필요한 양 (g)": round(grams),
            "개수": round(grams / m["piece"]),
            "얼음 대비": f"{grams / ice_grams:.1f}배",
            "음료": dilution,
        })
    return q, rows


# 6. 화면: 제목과 입력 위젯
st.title("🧊 냉각 소재 비교 계산기")
st.write("뜨거운 음료를 식힐 때 얼음, 재사용 얼음, 돌이 얼마나 필요한지 비교해요.")

col1, col2 = st.columns(2)
with col1:
    mass = st.number_input("음료 양 (g)", min_value=0.0, value=300.0, step=50.0)
    drink_temp = st.slider("음료 온도 (°C)", 0, 100, 80)
with col2:
    target = st.slider("목표 온도 (°C)", -10, 50, 10)
    start = st.slider("냉각 소재 처음 온도 (°C, 냉동실)", -30, 0, -18)

# 7. 입력이 바뀔 때마다 자동으로 다시 계산해서 결과 출력
error = check_input(mass, drink_temp, target, start)
if error:
    st.error(error)
else:
    q, rows = compare(mass, drink_temp, target, start)

    st.metric("음료가 내놓는 열", f"{q:,.0f} J")
    st.dataframe(rows, hide_index=True, width="stretch")

    st.write("**필요한 양 비교 (g)**")
    st.bar_chart({row["냉각 소재"]: row["필요한 양 (g)"] for row in rows}, horizontal=True)

    # 얼음 1g이 흡수하는 열을 현열·잠열·현열로 나눠서 보여줌 (잠열이 핵심)
    ice = MATERIALS["얼음"]
    steel = MATERIALS["스테인리스 큐브"]
    if target > ice["melt"]:
        solid = ice["c"] * (ice["melt"] - start)
        liquid = ice["c_liquid"] * (target - ice["melt"])
        ice_text = (f"얼음 1g = 0°C까지 {solid:.1f} J + **녹을 때 {ice['latent']} J (잠열)** + "
                    f"{target}°C까지 {liquid:.1f} J = {heat_per_gram(ice, start, target):.1f} J")
    else:
        ice_text = f"목표 온도가 0°C 이하라 얼음이 녹지 않아 현열만 계산: {heat_per_gram(ice, start, target):.1f} J"
    st.info(
        f"**왜 얼음이 훨씬 적게 필요할까?**\n\n{ice_text}\n\n"
        f"스테인리스 1g = 녹지 않아 온도가 오르는 만큼만 {steel['c']} × {target - start} = "
        f"{heat_per_gram(steel, start, target):.1f} J"
    )

st.caption("※ 컵이나 공기로 빠져나가는 열은 계산하지 않아서, 실제로는 조금 더 필요해요.")
