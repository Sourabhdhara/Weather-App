<div align="center">
  <img src="Weather app/favicon.png" alt="WeatherWise Logo" width="64" height="64">
  <h1>🌦️ WeatherWise 🌦️</h1>
  <p><b>A modern Tkinter desktop weather app with clean UI, hourly forecast, and 7-day outlook.</b></p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.x-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Tkinter-GUI-success.svg?style=for-the-badge" alt="Tkinter">
    <img src="https://img.shields.io/badge/Open--Meteo-API-informational.svg?style=for-the-badge" alt="Open-Meteo">
    <img src="https://img.shields.io/badge/PyInstaller-EXE_ready-orange.svg?style=for-the-badge" alt="PyInstaller">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License">
    <img src="https://img.shields.io/badge/Status-Icon_Safe-success.svg?style=for-the-badge" alt="Icon Safe">
  </p>

  <br>

  <b>[▶️ Run App](#-quick-start)</b> &nbsp;•&nbsp; <b>[📦 Build EXE](#-build-an-exe-pyinstaller)</b>
</div>

<hr>

## 🌟 Introduction

**WeatherWise** is a feature-rich desktop app built with **Tkinter** and powered by the **Open‑Meteo API**.  
It includes:
- 📍 **Auto-detect location** (IP-based)
- 🔎 **Search by city**
- 🌡️ **Current weather** (temperature, condition, wind, humidity, “feels like”)
- ⏱️ **Hourly forecast** (next 12 hours)
- 📅 **7-day forecast**
- 🖼️ **Window icon support** that works for **dev** and **PyInstaller EXE**

---

## 🚀 Amazing Features

<details>
<summary><b>📍 Auto Detect (IP-based)</b></summary>
<br>
Get the city automatically and fetch live weather instantly.
</details>

<details>
<summary><b>🔎 City Search</b></summary>
<br>
Type a city name and fetch coordinates + forecast using Open‑Meteo geocoding.
</details>

<details>
<summary><b>🌡️ Current Weather</b></summary>
<br>
A clean summary with temperature, weather condition, wind, humidity, and feels-like temperature.
</details>

<details>
<summary><b>⏱️ Hourly Forecast</b></summary>
<br>
Scrollable next 12 hours with dynamic weather icons.
</details>

<details>
<summary><b>📅 7-Day Outlook</b></summary>
<br>
Daily max/min temperature with icons for a quick weather overview.
</details>

<details>
<summary><b>🖼️ Reliable Window Icon (Dev + EXE)</b></summary>
<br>
Uses a PyInstaller-compatible `resource_path()` and tries **PNG first** with **ICO fallback**.
</details>

---

## 🛠️ Tech Stack

| Category | Used In |
| :---: | :---: |
| <img src="https://img.icons8.com/color/48/000000/python--v1.png" alt="Python"><br><b>Python</b> | Core app |
| <img src="https://img.icons8.com/color/48/000000/html-5--v1.png" alt="Tkinter"><br><b>Tkinter / ttk</b> | UI |
| <img src="https://img.icons8.com/color/48/000000/database.png" alt="Open-Meteo"><br><b>Open‑Meteo API</b> | Weather data |
    <img src="https://img.icons8.com/color/48/000000/python--v1.png" alt="PyInstaller"><br><b>PyInstaller</b> | Build EXE |

---

## ⚙️ Quick Start Guide

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App
```bash
python weather.py
```

---

## 📦 Build an EXE (PyInstaller)

### Build
```bash
pyinstaller weather.spec
```

### Output
Executable will typically be available under:
- `dist/weather.exe`

---

## 🖼️ Icon Handling Notes (Dev + EXE)

The app loads icons safely in both modes:
1. Tries `favicon.png` using `iconphoto` (Pillow required)
2. Falls back to `favicon.ico` using `iconbitmap`
3. Uses `sys._MEIPASS` via `resource_path()` so bundled resources work inside the `.exe`

---

## ✅ Testing Checklist (Recommended)

Before sharing the EXE, verify:
- [ ] Dev mode: app opens and window icon appears
- [ ] Dev mode: PNG loads; ICO fallback works when needed
- [ ] EXE: icon loads correctly from PyInstaller bundle (`sys._MEIPASS`)
- [ ] UX: Auto Detect, Search, Refresh buttons work
- [ ] UX: Tabs render correctly (Current / Hourly / 7‑Day)

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
