# 냉각 소재 비교 계산기 창 버전 (tkinter)
# 파이썬에 기본으로 들어 있는 tkinter만 써서 설치 없이 Run(F5)으로 실행됨
# 계산 부분은 콘솔 버전(2901_김연우.py)과 같음
import tkinter as tk
from tkinter import ttk

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


# 4. 입력값 검사: 문제가 있으면 안내 문장, 없으면 None을 돌려줌 (콘솔 버전 83~90행과 같은 조건)
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


# 5. 소재마다 필요한 양을 계산해 표의 행 리스트로 돌려줌
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
            dilution = f"{grams / (mass + grams) * 100:.0f}% 묽어짐"
        else:
            dilution = "안 묽어짐"
        rows.append((name, per_gram, grams, grams / m["piece"], grams / ice_grams, dilution))
    return q, rows


# 6. 계산 버튼을 누르면 실행되는 함수: 입력을 읽고 → 검사하고 → 결과를 화면에 그림
def calculate():
    try:
        mass = float(entries["mass"].get())
        drink_temp = float(entries["drink_temp"].get())
        target = float(entries["target"].get())
        start = float(entries["start"].get())
    except ValueError:
        show_message("숫자로 입력하세요.")
        return

    error = check_input(mass, drink_temp, target, start)
    if error:
        show_message(error)
        return

    q, rows = compare(mass, drink_temp, target, start)
    heat_label.config(text=f"음료가 내놓는 열: {q:,.0f} J", fg="black")

    # 표 다시 채우기
    table.delete(*table.get_children())
    for name, per_gram, grams, pieces, ratio, dilution in rows:
        table.insert("", "end", values=(name, f"{per_gram:.1f}", f"{grams:,.0f}",
                                        f"{pieces:.0f}", f"{ratio:.1f}배", dilution))

    # 막대그래프 다시 그리기 (가장 많이 필요한 소재가 끝까지 닿도록 비율 맞춤)
    chart.delete("all")
    biggest = max(row[2] for row in rows)
    for i, (name, per_gram, grams, pieces, ratio, dilution) in enumerate(rows):
        y = 15 + i * 32
        length = grams / biggest * 420
        chart.create_text(150, y + 10, text=name, anchor="e")
        chart.create_rectangle(160, y, 160 + length, y + 20, fill="#1f77b4", outline="")
        chart.create_text(165 + length, y + 10, text=f"{grams:,.0f} g", anchor="w")

    # 얼음과 스테인리스 1g이 흡수하는 열 비교 (잠열이 핵심)
    ice = MATERIALS["얼음"]
    steel = MATERIALS["스테인리스 큐브"]
    if target > ice["melt"]:
        solid = ice["c"] * (ice["melt"] - start)
        liquid = ice["c_liquid"] * (target - ice["melt"])
        ice_text = (f"얼음 1g = 0°C까지 {solid:.1f} J + 녹을 때 {ice['latent']} J (잠열) + "
                    f"{target:g}°C까지 {liquid:.1f} J = {heat_per_gram(ice, start, target):.1f} J")
    else:
        ice_text = f"목표 온도가 0°C 이하라 얼음이 녹지 않아 현열만 계산: {heat_per_gram(ice, start, target):.1f} J"
    steel_text = (f"스테인리스 1g = 녹지 않아 온도가 오르는 만큼만 {steel['c']} × {target - start:g} = "
                  f"{heat_per_gram(steel, start, target):.1f} J")
    info_label.config(text=f"왜 얼음이 훨씬 적게 필요할까?\n{ice_text}\n{steel_text}")


# 7. 잘못된 입력일 때 빨간 글씨로 안내하고 결과를 지움
def show_message(text):
    heat_label.config(text=text, fg="red")
    table.delete(*table.get_children())
    chart.delete("all")
    info_label.config(text="")


# 8. 화면 만들기
window = tk.Tk()
window.title("냉각 소재 비교 계산기")
window.geometry("760x640")

tk.Label(window, text="냉각 소재 비교 계산기", font=("", 20, "bold")).pack(pady=(15, 0))
tk.Label(window, text="뜨거운 음료를 식힐 때 얼음, 재사용 얼음, 돌이 얼마나 필요한지 비교해요.").pack()

# 입력 칸 4개 (처음 값 = 콘솔 버전의 기본값)
form = tk.Frame(window)
form.pack(pady=10)
fields = [
    ("mass", "음료 양 (g)", "300"),
    ("drink_temp", "음료 온도 (°C)", "80"),
    ("target", "목표 온도 (°C)", "10"),
    ("start", "냉각 소재 처음 온도 (°C, 냉동실)", "-18"),
]
entries = {}
for i, (key, label, default) in enumerate(fields):
    tk.Label(form, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky="e", padx=5, pady=3)
    entry = tk.Entry(form, width=8)
    entry.insert(0, default)
    entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=3)
    entry.bind("<Return>", lambda event: calculate())  # Enter를 눌러도 계산
    entries[key] = entry

tk.Button(window, text="계산하기", command=calculate, bg="#ff4b4b", fg="white",
          font=("", 12, "bold")).pack()

heat_label = tk.Label(window, text="", font=("", 14, "bold"))
heat_label.pack(pady=8)

# 결과 표
columns = ("냉각 소재", "1g당 흡수열 (J)", "필요한 양 (g)", "개수", "얼음 대비", "음료")
table = ttk.Treeview(window, columns=columns, show="headings", height=4)
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150 if col == "냉각 소재" else 110, anchor="center")
table.pack(padx=15)

# 막대그래프
chart = tk.Canvas(window, width=720, height=140)
chart.pack(pady=5)

info_label = tk.Label(window, text="", justify="left", bg="#e8f1fb", fg="#0b4f8a", padx=10, pady=8)
info_label.pack(fill="x", padx=15)

tk.Label(window, text="※ 컵이나 공기로 빠져나가는 열은 계산하지 않아서, 실제로는 조금 더 필요해요.",
         fg="gray").pack(pady=5)

calculate()  # 처음 열 때 기본값으로 한 번 계산해서 보여줌
window.mainloop()
