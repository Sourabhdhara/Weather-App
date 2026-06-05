#!/usr/bin/env python3
"""
WeatherWise CLI - A simple command-line weather application.
Fetches current conditions, hourly, and daily forecasts using Open-Meteo API.
"""

import argparse
import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

import requests

# -------------------------------
# Weather icon mapping (WMO codes)
# -------------------------------
def get_weather_icon(code: int) -> Tuple[str, str]:
    """Return emoji and description for WMO weather code."""
    if code == 0:
        return "☀️", "Clear sky"
    if code in (1, 2):
        return "🌤️", "Mainly clear"
    if code == 3:
        return "☁️", "Overcast"
    if code in (45, 48):
        return "🌫️", "Fog"
    if code in (51, 53, 55):
        return "🌦️", "Drizzle"
    if code in (56, 57):
        return "🌧️", "Freezing drizzle"
    if code in (61, 63, 65):
        return "🌧️", "Rain"
    if code in (66, 67):
        return "🌨️", "Freezing rain"
    if code in (71, 73, 75):
        return "❄️", "Snow"
    if code == 77:
        return "🌨️", "Snow grains"
    if code in (80, 81, 82):
        return "🌧️", "Rain showers"
    if code in (85, 86):
        return "❄️", "Snow showers"
    if code == 95:
        return "⛈️", "Thunderstorm"
    if code in (96, 99):
        return "⛈️", "Thunderstorm with hail"
    return "🌈", "Unknown"


# -------------------------------
# Geolocation (IP-based)
# -------------------------------
def get_location_from_ip() -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Get approximate location using IP geolocation."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=10)
        data = response.json()
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city")
            country = data.get("country")
            location_name = f"{city}, {country}" if city else "Unknown"
            return lat, lon, location_name
    except Exception:
        pass
    return None, None, None


# -------------------------------
# Geocoding (city name to coordinates)
# -------------------------------
def geocode_city(city_name: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Convert city name to coordinates using Open-Meteo geocoding API."""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            name = result.get("name", city_name)
            country = result.get("country", "")
            location_name = f"{name}, {country}" if country else name
            return lat, lon, location_name
    except Exception:
        pass
    return None, None, None


# -------------------------------
# Fetch weather data from Open-Meteo
# -------------------------------
def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """Retrieve current, hourly, and daily weather data."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "temperature_2m,weathercode,windspeed_10m,relativehumidity_2m",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# -------------------------------
# Unit conversions
# -------------------------------
def convert_temperature(celsius: float, unit: str) -> Tuple[float, str]:
    """Convert Celsius to Fahrenheit if needed."""
    if unit.lower() == "c":
        return celsius, "°C"
    return celsius * 9 / 5 + 32, "°F"


def convert_wind(kmh: float, unit: str) -> Tuple[float, str]:
    """Convert km/h to mph if needed."""
    if unit.lower() == "kmh":
        return kmh, "km/h"
    return kmh * 0.621371, "mph"


# -------------------------------
# Display functions
# -------------------------------
def display_current(data: Dict[str, Any], temp_unit: str, wind_unit: str) -> None:
    """Show current weather conditions."""
    current = data.get("current_weather", {})
    if not current:
        print("No current weather data available.")
        return

    temp_c = current.get("temperature")
    wind_kmh = current.get("windspeed")
    weather_code = current.get("weathercode")
    icon, condition = get_weather_icon(weather_code)

    temp_val, temp_sym = convert_temperature(temp_c, temp_unit)
    wind_val, wind_sym = convert_wind(wind_kmh, wind_unit)

    print("\n📍 Current Weather")
    print("━" * 40)
    print(f"{icon}  {condition}")
    print(f"🌡️  Temperature: {temp_val:.1f}{temp_sym}")
    print(f"💨 Wind: {wind_val:.1f} {wind_sym}")

    # Extract humidity from hourly data (nearest hour)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    humidities = hourly.get("relativehumidity_2m", [])
    if times and humidities:
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        for i, t in enumerate(times):
            try:
                t_dt = datetime.fromisoformat(t)
                if t_dt >= now:
                    print(f"💧 Humidity: {humidities[i]}%")
                    break
            except Exception:
                continue
    print("━" * 40)


def display_hourly(data: Dict[str, Any], temp_unit: str, wind_unit: str, hours: int = 12) -> None:
    """Show hourly forecast for the next `hours` hours."""
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    winds = hourly.get("windspeed_10m", [])
    codes = hourly.get("weathercode", [])

    if not times:
        print("No hourly forecast data available.")
        return

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_idx = 0
    for i, t_str in enumerate(times):
        try:
            t_dt = datetime.fromisoformat(t_str)
            if t_dt >= now:
                start_idx = i
                break
        except Exception:
            continue

    end_idx = min(start_idx + hours, len(times))
    print(f"\n⏱️  Hourly Forecast (next {end_idx - start_idx} hours)")
    print("━" * 60)

    for i in range(start_idx, end_idx):
        time_str = times[i]
        try:
            dt = datetime.fromisoformat(time_str)
            hour_label = dt.strftime("%H:%M")
        except Exception:
            hour_label = time_str[11:16] if len(time_str) > 11 else time_str

        temp_c = temps[i] if i < len(temps) else None
        wind_kmh = winds[i] if i < len(winds) else None
        code = codes[i] if i < len(codes) else 0
        icon, _ = get_weather_icon(code)

        temp_val, temp_sym = convert_temperature(temp_c, temp_unit) if temp_c is not None else (None, "")
        wind_val, wind_sym = convert_wind(wind_kmh, wind_unit) if wind_kmh is not None else (None, "")

        line = f"{hour_label}  {icon}  "
        if temp_val is not None:
            line += f"{temp_val:.1f}{temp_sym}  "
        if wind_val is not None:
            line += f"💨 {wind_val:.1f}{wind_sym}"
        print(line)

    print("━" * 60)


def display_daily(data: Dict[str, Any], temp_unit: str, wind_unit: str, days: int = 7) -> None:
    """Show daily forecast for the next `days` days."""
    daily = data.get("daily", {})
    day_times = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    winds = daily.get("windspeed_10m_max", [])
    codes = daily.get("weathercode", [])

    if not day_times:
        print("No daily forecast data available.")
        return

    print(f"\n📅 {days}-Day Forecast")
    print("━" * 70)

    for idx in range(min(len(day_times), days)):
        day_str = day_times[idx]
        try:
            dt = datetime.fromisoformat(day_str)
            day_name = dt.strftime("%A")
            date_str = dt.strftime("%d/%m")
        except Exception:
            day_name = day_str[:10]
            date_str = ""

        max_c = max_temps[idx] if idx < len(max_temps) else None
        min_c = min_temps[idx] if idx < len(min_temps) else None
        wind_kmh = winds[idx] if idx < len(winds) else None
        code = codes[idx] if idx < len(codes) else 0
        icon, desc = get_weather_icon(code)

        max_val, max_sym = convert_temperature(max_c, temp_unit) if max_c is not None else (None, "")
        min_val, min_sym = convert_temperature(min_c, temp_unit) if min_c is not None else (None, "")
        wind_val, wind_sym = convert_wind(wind_kmh, wind_unit) if wind_kmh is not None else (None, "")

        print(f"{day_name:10} {date_str:6} {icon}  {desc:18} ", end="")
        if max_val is not None and min_val is not None:
            print(f"↑ {max_val:.1f}{max_sym}  ↓ {min_val:.1f}{min_sym}  ", end="")
        if wind_val is not None:
            print(f"💨 {wind_val:.1f}{wind_sym}", end="")
        print()

    print("━" * 70)


# -------------------------------
# Main CLI logic
# -------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="WeatherWise CLI - Get weather forecasts from the command line."
    )
    parser.add_argument("--city", type=str, help="City name (e.g., 'London')")
    parser.add_argument("--auto", action="store_true", help="Auto-detect location via IP")
    parser.add_argument("--temp-unit", choices=["c", "f"], default="c", help="Temperature unit (c = Celsius, f = Fahrenheit)")
    parser.add_argument("--wind-unit", choices=["kmh", "mph"], default="kmh", help="Wind speed unit")
    parser.add_argument("--hourly", action="store_true", help="Show hourly forecast")
    parser.add_argument("--daily", action="store_true", help="Show daily forecast")
    parser.add_argument("--all", action="store_true", help="Show current, hourly, and daily forecasts")

    args = parser.parse_args()

    # Determine location
    lat = lon = None
    location_name = None

    if args.city:
        print(f"🔍 Searching for '{args.city}'...")
        lat, lon, location_name = geocode_city(args.city)
        if lat is None:
            print(f"❌ Error: City '{args.city}' not found.")
            sys.exit(1)
    elif args.auto:
        print("📍 Auto-detecting location via IP...")
        lat, lon, location_name = get_location_from_ip()
        if lat is None:
            print("❌ Error: Could not auto-detect location.")
            sys.exit(1)
    else:
        # Interactive prompt
        print("🌦️  WeatherWise CLI")
        print("Press Enter to auto-detect, or type a city name: ", end="")
        user_input = input().strip()
        if user_input == "":
            print("📍 Auto-detecting...")
            lat, lon, location_name = get_location_from_ip()
            if lat is None:
                print("❌ Auto-detection failed. Please restart and enter a city name.")
                sys.exit(1)
        else:
            print(f"🔍 Searching for '{user_input}'...")
            lat, lon, location_name = geocode_city(user_input)
            if lat is None:
                print(f"❌ City '{user_input}' not found.")
                sys.exit(1)

    print(f"✅ Location: {location_name}")

    # Fetch weather data
    try:
        weather_data = fetch_weather_data(lat, lon)
    except Exception as e:
        print(f"❌ Failed to fetch weather data: {e}")
        sys.exit(1)

    # Display requested forecasts
    if args.all:
        display_current(weather_data, args.temp_unit, args.wind_unit)
        display_hourly(weather_data, args.temp_unit, args.wind_unit)
        display_daily(weather_data, args.temp_unit, args.wind_unit)
    else:
        display_current(weather_data, args.temp_unit, args.wind_unit)
        if args.hourly:
            display_hourly(weather_data, args.temp_unit, args.wind_unit)
        if args.daily:
            display_daily(weather_data, args.temp_unit, args.wind_unit)


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")   # <-- add this line
    