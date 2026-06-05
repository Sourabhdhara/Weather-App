<div align="center">

# ☁️ WeatherWise - Modern Weather App

<img src="image.png" alt="WeatherWise Banner" width="100%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

**A sleek, responsive weather application built with Python Flask, HTML5, CSS3, and JavaScript. Get accurate forecasts, hourly & daily predictions, and unit conversions – all in a beautiful glass‑morphic UI.**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-lightgrey.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Open-Meteo](https://img.shields.io/badge/API-OpenMeteo-00b4d8?style=for-the-badge&logo=openstreetmap&logoColor=white)](https://open-meteo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[**🌐 Try Live Demo**](#) • [**Explore Features**](#-core-features) • [**Quick Start**](#-quick-start) • [**Screenshots**](#-screenshots) • [**API Documentation**](#-api-endpoints)

</div>

---

## 🌟 About The Project

**WeatherWise** is a full‑stack weather application that combines a robust Python backend (Flask) with a modern, interactive frontend. It consumes the free and open **Open‑Meteo API** to deliver real‑time weather data, 24‑hour hourly forecasts, and 7‑day predictions.

### 🔑 Key Highlights:
- 🎨 **Glass‑morphic UI** – Visually appealing, responsive design with smooth animations.
- 🌍 **Geolocation Support** – Auto‑detects your location via browser or IP fallback.
- 🔍 **City Search** – Search any city worldwide with fast geocoding.
- 📊 **Unit Toggle** – Switch between °C/°F and km/h/mph on the fly.
- ⏱️ **Hourly & Daily Forecasts** – Scrollable hourly cards and a clean 7‑day grid.
- 🚀 **No Database** – Lightweight, runs with JSON and API calls.

---

## 🚀 Quick Start

Get the project running on your local machine in seconds.

### Prerequisites
- **Python 3.7+** installed.
- A modern web browser.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/weatherwise.git
cd weatherwise

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Flask application
python app.py
