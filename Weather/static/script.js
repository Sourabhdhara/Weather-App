// static/script.js
// Global state
let currentWeatherData = null;  // stores metric units (C, km/h)
let currentLocation = { lat: null, lon: null, name: "Unknown" };
let tempUnit = "C";
let windUnit = "kmh";

// DOM Elements
const cityInput = document.getElementById("cityInput");
const searchBtn = document.getElementById("searchBtn");
const autoDetectBtn = document.getElementById("autoDetectBtn");
const refreshBtn = document.getElementById("refreshBtn");
const locationNameEl = document.getElementById("locationName");
const updateTimeEl = document.getElementById("updateTime");
const currentIcon = document.getElementById("currentIcon");
const currentTemp = document.getElementById("currentTemp");
const conditionText = document.getElementById("conditionText");
const windValue = document.getElementById("windValue");
const humidityValue = document.getElementById("humidityValue");
const feelsLikeValue = document.getElementById("feelsLikeValue");
const statusMsg = document.getElementById("statusMsg");
const tempUnitSymbol = document.getElementById("tempUnitSymbol");
const feelsUnit = document.getElementById("feelsUnit");
const windUnitSpan = document.getElementById("windUnit");

// Tab elements
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

// Unit buttons
const tempUnitBtns = document.querySelectorAll(".unit-btn");
const windUnitBtns = document.querySelectorAll(".wind-btn");

// Helper: Update status
function setStatus(msg, isError = false) {
    statusMsg.innerHTML = `<i class="fas ${isError ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i> ${msg}`;
    if (isError) console.error(msg);
}

// Weather icon mapping (WMO codes) - only for hourly/daily fallback
// For current weather we use backend's icon (which handles night)
function getWeatherIcon(code) {
    const icons = {
        0: "☀️", 1: "🌤️", 2: "🌤️", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️",
        56: "🌧️", 57: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        66: "🌨️", 67: "🌨️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "🌨️",
        80: "🌧️", 81: "🌧️", 82: "🌧️",
        85: "❄️", 86: "❄️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    };
    return icons[code] || "🌈";
}

function getWeatherDescription(code) {
    const desc = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Fog",
        51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
        56: "Freezing drizzle", 57: "Freezing drizzle",
        61: "Rain", 63: "Rain", 65: "Rain",
        66: "Freezing rain", 67: "Freezing rain",
        71: "Snow", 73: "Snow", 75: "Snow", 77: "Snow grains",
        80: "Rain showers", 81: "Rain showers", 82: "Rain showers",
        85: "Snow showers", 86: "Snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail"
    };
    return desc[code] || "Unknown";
}

// Unit conversions
function convertTemp(celsius) {
    if (tempUnit === "C") return celsius;
    return celsius * 9/5 + 32;
}

function convertWind(kmh) {
    if (windUnit === "kmh") return kmh;
    return kmh * 0.621371;
}

// Update all UI based on stored metric data
function updateUI() {
    if (!currentWeatherData) return;
    
    const current = currentWeatherData.current;
    const tempC = current.temp_c;
    const windK = current.wind_kmh;
    const feelsC = current.feels_like_c;
    const humidity = current.humidity;
    
    // Use icon and condition from backend (already day/night aware)
    const iconEmoji = current.icon;          // from backend
    const conditionDesc = current.condition; // from backend
    
    const convertedTemp = convertTemp(tempC);
    const convertedWind = convertWind(windK);
    const convertedFeels = convertTemp(feelsC);
    
    currentIcon.textContent = iconEmoji;
    currentTemp.textContent = convertedTemp.toFixed(1);
    conditionText.textContent = conditionDesc;
    windValue.textContent = convertedWind.toFixed(1);
    humidityValue.textContent = humidity !== null ? humidity : "--";
    feelsLikeValue.textContent = convertedFeels.toFixed(1);
    
    tempUnitSymbol.textContent = tempUnit === "C" ? "°C" : "°F";
    feelsUnit.textContent = tempUnit === "C" ? "°C" : "°F";
    windUnitSpan.textContent = windUnit === "kmh" ? "km/h" : "mph";
    
    locationNameEl.textContent = currentLocation.name;
    updateTimeEl.innerHTML = `<i class="far fa-clock"></i> Last update: ${currentWeatherData.last_update}`;
    
    // Update hourly cards
    updateHourlyUI();
    // Update daily cards
    updateDailyUI();
}

function updateHourlyUI() {
    const container = document.getElementById("hourlyContainer");
    if (!currentWeatherData || !currentWeatherData.hourly.length) {
        container.innerHTML = '<div class="loading-spinner">No hourly data available</div>';
        return;
    }
    
    let html = '<div class="horizontal-scroll">';
    for (let item of currentWeatherData.hourly) {
        const tempC = item.temp;
        const windK = item.wind;
        const code = item.weathercode;
        const icon = getWeatherIcon(code);  // hourly uses generic icons (day assumed)
        const tempVal = convertTemp(tempC);
        const windVal = convertWind(windK);
        const tempUnitSym = tempUnit === "C" ? "°C" : "°F";
        const windUnitSym = windUnit === "kmh" ? "km/h" : "mph";
        
        html += `
            <div class="hourly-card">
                <div class="hourly-time">${item.time}</div>
                <div class="hourly-icon">${icon}</div>
                <div class="hourly-temp">${tempVal.toFixed(1)}${tempUnitSym}</div>
                <div class="hourly-wind">💨 ${windVal.toFixed(1)} ${windUnitSym}</div>
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

function updateDailyUI() {
    const container = document.getElementById("dailyContainer");
    if (!currentWeatherData || !currentWeatherData.daily.length) {
        container.innerHTML = '<div class="loading-spinner">No daily forecast available</div>';
        return;
    }
    
    let html = '<div class="daily-grid">';
    for (let item of currentWeatherData.daily) {
        const maxC = item.max_temp;
        const minC = item.min_temp;
        const windK = item.wind;
        const code = item.weathercode;
        const icon = getWeatherIcon(code);  // daily uses generic icons
        const maxVal = convertTemp(maxC);
        const minVal = convertTemp(minC);
        const windVal = convertWind(windK);
        const tempSym = tempUnit === "C" ? "°C" : "°F";
        const windSym = windUnit === "kmh" ? "km/h" : "mph";
        
        html += `
            <div class="daily-card">
                <div class="daily-day">${item.day}</div>
                <div class="daily-date">${item.date}</div>
                <div class="daily-icon">${icon}</div>
                <div class="daily-temp-max">↑ ${maxVal.toFixed(1)}${tempSym}</div>
                <div class="daily-temp-min">↓ ${minVal.toFixed(1)}${tempSym}</div>
                <div class="daily-wind">💨 ${windVal.toFixed(1)} ${windSym}</div>
            </div>
        `;
    }
    html += '</div>';
    container.innerHTML = html;
}

// Fetch weather from backend (metric)
async function fetchWeather(lat, lon, locationName) {
    setStatus(`Fetching weather for ${locationName}...`);
    try {
        const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Weather fetch failed");
        }
        const data = await response.json();
        currentWeatherData = data;
        currentLocation = { lat, lon, name: locationName };
        updateUI();
        setStatus(`✅ Updated: ${locationName}`);
    } catch (err) {
        setStatus(`❌ Error: ${err.message}`, true);
        console.error(err);
    }
}

// Search city
async function searchCity() {
    const city = cityInput.value.trim();
    if (!city) {
        setStatus("Please enter a city name", true);
        return;
    }
    setStatus(`Searching for '${city}'...`);
    try {
        const res = await fetch(`/api/search?city=${encodeURIComponent(city)}`);
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || "City not found");
        }
        const data = await res.json();
        currentLocation = { lat: data.lat, lon: data.lon, name: data.name };
        await fetchWeather(data.lat, data.lon, data.name);
    } catch (err) {
        setStatus(`Search failed: ${err.message}`, true);
    }
}

// Auto detect: browser geolocation -> reverse geocode -> weather, fallback to IP
async function autoDetect() {
    setStatus("Detecting your location...");
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            try {
                const revRes = await fetch(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
                const revData = await revRes.json();
                const locationName = revData.name || `${lat.toFixed(2)}, ${lon.toFixed(2)}`;
                await fetchWeather(lat, lon, locationName);
            } catch {
                await fetchWeather(lat, lon, `Coordinates (${lat.toFixed(2)}, ${lon.toFixed(2)})`);
            }
        }, async () => {
            // Fallback to IP detection
            await ipLocationFallback();
        });
    } else {
        await ipLocationFallback();
    }
}

async function ipLocationFallback() {
    try {
        const res = await fetch("/api/ip-location");
        if (!res.ok) throw new Error("IP detection failed");
        const data = await res.json();
        await fetchWeather(data.lat, data.lon, data.name);
    } catch (err) {
        setStatus("Could not detect location automatically. Please search manually.", true);
    }
}

async function refreshWeather() {
    if (currentLocation.lat && currentLocation.lon) {
        await fetchWeather(currentLocation.lat, currentLocation.lon, currentLocation.name);
    } else {
        setStatus("No location data. Use auto-detect or search.", true);
    }
}

// Unit toggles
function setupUnitToggles() {
    tempUnitBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tempUnitBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            tempUnit = btn.getAttribute("data-unit");
            updateUI();
        });
    });
    
    windUnitBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            windUnitBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            windUnit = btn.getAttribute("data-wind");
            updateUI();
        });
    });
}

// Tab switching
function setupTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            tabContents.forEach(tab => tab.classList.remove("active"));
            document.getElementById(`${tabId}Tab`).classList.add("active");
        });
    });
}

// Event listeners
searchBtn.addEventListener("click", searchCity);
cityInput.addEventListener("keypress", (e) => { if (e.key === "Enter") searchCity(); });
autoDetectBtn.addEventListener("click", autoDetect);
refreshBtn.addEventListener("click", refreshWeather);

// Initialize
function init() {
    setupUnitToggles();
    setupTabs();
    autoDetect(); // initial auto detection
}

init();
