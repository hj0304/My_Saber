<div align="center">

[🇺🇸 English](README.md) | [🇰🇷 Korean](README_kr.md)

</div>

# My Saber: Baseball Analytics Platform ⚾️

> **데이터로 보는 야구의 새로운 관점** > KBO/MLB 데이터 분석부터 3D 피칭 시뮬레이션까지 제공하는 웹 애플리케이션입니다.

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)

## 📖 프로젝트 소개
**My Saber**는 야구 데이터를 심층적으로 분석하여 인사이트를 제공하는 플랫폼입니다. 단순히 기록을 보여주는 것을 넘어, '강한 2번 타자 이론', '불펜 투수 중요도(gmLI)', '선수 가치 평가(Surplus Value)' 등 세이버메트릭스 관점에서 야구를 재해석합니다. 실제 MLB Statcast 데이터를 활용한 피칭 시뮬레이터와 데이터 수집 현황을 볼 수 있는 대시보드도 포함되어 있습니다.

## ✨ 주요 기능 (Key Features)

### 📊 1. 세이버메트릭스 분석 (Analysis)
* **강한 2번 타자 (Strong 2nd Batter):** 현대 야구의 타순 트렌드를 분석하고 KBO와 MLB의 타순별 OPS/wRC+ 흐름을 비교합니다.
* **선발 투수 메타 (Pitcher Meta):** 이닝 소화(IP)와 실점(Runs)에 따른 팀의 기대 승률(Win Rate)을 히트맵으로 시각화합니다.
* **불펜 투수 지표 (Relief Metrics):** 승리 확률 기여도(WPA)와 등판 상황 중요도(gmLI)를 통해 '진짜 에이스' 불펜을 찾아냅니다.
* **선수 가치 평가 (Cost Effectiveness):** 선수의 연봉(Salary) 대비 실제 활약 가치(Dollars)를 산출하여 '가성비(Surplus Value)' 선수를 분석합니다.
* **샘플 사이즈 신뢰도 (Sample Size):** 타석/투구 수에 따라 야구 기록이 통계적으로 유의미해지는 시점(Stabilization Point)을 분석합니다.

### 🎮 2. 시뮬레이션 (Simulation)
* **피칭 터널 시뮬레이터:** 실제 MLB 투구 추적 데이터(Statcast)를 기반으로 투수의 공 궤적을 3D 환경(또는 시각화)에서 체험할 수 있습니다.

### 📈 3. 데이터 대시보드 (Dashboard)
* **Streamlit 기반 대시보드:** 2016-2025년 수집된 MLB 데이터의 규모, 구종 분포, 누적 투구 수 상위 투수 등을 한눈에 파악할 수 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
* **Python 3.11+**
* **Django 6.0**: 웹 프레임워크
* **Pandas / NumPy**: 데이터 전처리 및 분석
* **PyBaseball**: MLB 데이터 수집 라이브러리

### Frontend
* **HTML5 / CSS3**
* **TailwindCSS**: UI 스타일링 (`animate-fade-in-up`, 그라디언트 효과 등 활용)
* **Chart.js / Plotly**: 데이터 시각화

### Data Science & Tools
* **Streamlit**: 데이터 현황 대시보드
* **Scikit-learn**: 데이터 분석 모델링
* **SQLite**: 데이터베이스 (개발 환경)

---

## 🚀 설치 및 실행 (Getting Started)

이 프로젝트는 Django 웹 서버와 Streamlit 대시보드로 구성되어 있습니다.

### 1. 사전 요구 사항
* Python 3.11 이상이 설치되어 있어야 합니다.

### 2. 프로젝트 클론 및 패키지 설치
```bash
# 레포지토리 클론
git clone [https://github.com/hj0304/my_saber.git](https://github.com/hj0304/my_saber.git)
cd my_saber

# 가상환경 생성 (선택 사항)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 필수 패키지 설치
pip install -r requirements.txt
3. Django 서버 실행 (웹 애플리케이션)
데이터 분석 및 시뮬레이션 기능을 사용하려면 Django 서버를 실행하세요.

Bash

# 데이터베이스 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
브라우저에서 http://127.0.0.1:8000/ 으로 접속합니다.

4. Streamlit 대시보드 실행 (데이터 현황)
수집된 데이터 통계를 확인하려면 Streamlit을 실행하세요.

Bash

streamlit run dashboard/app.py
브라우저에서 http://localhost:8501/ 으로 접속합니다.

📂 프로젝트 구조 (Structure)
Bash

my_saber/
├── analysis/       # 분석 기능 앱 (강한 2번, 투수 지표 등)
├── simulation/     # 시뮬레이션 앱 (피칭 터널 등)
├── core/           # 메인 랜딩 페이지 및 공통 템플릿
├── dashboard/      # Streamlit 대시보드 코드
├── data_science/   # 데이터 수집(ETL) 및 분석 스크립트
├── static/         # 정적 파일 (CSS, JS, Images)
├── templates/      # Django HTML 템플릿
└── manage.py       # Django 관리 스크립트


📝 License
This project is licensed under the MIT License.