# 📱 스마트폰 과열 진단 웹앱

주변 온도, 충전 방식, 케이스 사용, 충전 중 게임 여부를 고르면 배터리 과열 위험 점수(0~9점)를 계산해 안전·주의·위험으로 알려주는 Streamlit 웹앱입니다.

- `app.py` — 웹앱 코드
- `웹앱코드설명.md` — 코드 설명

실행: `pip install streamlit` 후 `streamlit run app.py`

---

# 🧊 냉각 소재 비교 계산기 웹앱

음료 양·온도, 목표 온도, 냉각 소재 온도를 고르면 얼음·젤 아이스팩·스테인리스 큐브·위스키 스톤이 각각 얼마나 필요한지 열평형으로 비교하는 Streamlit 웹앱입니다.

- `cooling_app.py` — 웹앱 코드
- `cooling_tk.py` — 설치 없이 파이썬만으로 실행되는 창 버전 (tkinter)
- `냉각계산기_웹앱코드설명.md` — 코드 설명, 배포 방법, 발표 순서

실행: `pip install streamlit` 후 `cooling_app.py`를 파이썬에서 Run(F5), 또는 `streamlit run cooling_app.py`
