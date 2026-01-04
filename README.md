<div align="center">

[🇺🇸 English](README.md) | [🇰🇷 Korean](README_kr.md)

</div>


# My Saber: Baseball Analytics Platform ⚾️

> **A New Perspective on Baseball with Data**
> A web application providing KBO/MLB data analysis and 3D pitching simulation.

<div align="center">

[🇺🇸 English](README.md) | [🇰🇷 Korean](README_kr.md)

</div>

---

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 Introduction
**My Saber** is a platform that analyzes baseball data to provide deep insights. Beyond displaying simple stats, it reinterprets baseball through Sabermetrics perspectives such as 'Strong 2nd Batter Theory', 'Bullpen Importance (gmLI)', and 'Player Valuation (Surplus Value)'. It also features a pitching simulator based on actual MLB Statcast data and a dashboard for data collection status.

## ✨ Key Features

### 📊 1. Sabermetrics Analysis
* **Strong 2nd Batter:** Analyzes modern lineup trends and compares OPS/wRC+ flows by batting order in KBO and MLB.
* **Pitcher Meta:** Visualizes team Win Expectancy based on IP (Innings Pitched) and Runs allowed using heatmaps.
* **Relief Metrics:** Identifies true 'ace' relievers using WPA (Win Probability Added) and gmLI (Leverage Index).
* **Cost Effectiveness:** Evaluates player efficiency by comparing Salary vs. actual Performance Value (Dollars) to find 'Surplus Value'.
* **Sample Size & Reliability:** Analyzes the Stabilization Point where baseball stats become statistically significant based on PA/Pitch counts.

### 🎮 2. Simulation
* **Pitch Tunneling Simulator:** Experience 3D pitch trajectories based on actual MLB Statcast tracking data.

### 📈 3. Data Dashboard
* **Streamlit Dashboard:** Provides an overview of collected data (2016-2025), including pitch type distribution and top pitchers by pitch count.

---

## 🛠 Tech Stack

### Backend
* **Python 3.11+**
* **Django 6.0**: Web Framework
* **Pandas / NumPy**: Data Processing & Analysis
* **PyBaseball**: MLB Data Collection Library

### Frontend
* **HTML5 / CSS3**
* **TailwindCSS**: UI Styling
* **Chart.js / Plotly**: Data Visualization

### Data Science & Tools
* **Streamlit**: Data Status Dashboard
* **Scikit-learn**: Analysis Modeling
* **SQLite**: Database (Development)

---

## 🚀 Getting Started

This project consists of a Django web server and a Streamlit dashboard.

### 1. Prerequisites
* Python 3.11 or higher is required.

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/hj0304/my_saber.git](https://github.com/hj0304/my_saber.git)
cd my_saber

# Create virtual environment (Optional)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

3. Run Django Server (Web Application)
Run the Django server to access analysis and simulation features.

Bash

# Database migration
python manage.py migrate

# Run server
python manage.py runserver
Access the app at http://127.0.0.1:8000/.

4. Run Streamlit Dashboard (Data Overview)
Run Streamlit to view data statistics.

Bash

streamlit run dashboard/app.py
Access the dashboard at http://localhost:8501/.

📂 Directory Structure
Bash

my_saber/
├── analysis/       # Analysis Apps (Strong 2nd, Pitcher Metrics, etc.)
├── simulation/     # Simulation Apps (Pitch Tunnel, etc.)
├── core/           # Main Landing Page & Common Templates
├── dashboard/      # Streamlit Dashboard Code
├── data_science/   # Data Collection (ETL) & Analysis Scripts
├── static/         # Static Files (CSS, JS, Images)
├── templates/      # Django HTML Templates
└── manage.py       # Django Management Script
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.