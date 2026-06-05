# app.py
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ---------- Helper Functions ----------
def get_weather_icon(code):
    """Return emoji and description for WMO weather code"""
    mapping = {
        0: ("☀️", "Clear sky"),
        1: ("🌤️", "Mainly clear"),
        2: ("🌤️", "Partly cloudy"),
        3: ("☁️", "Overcast"),
        45: ("🌫️", "Fog"),
        48: ("🌫️", "Fog"),
        51: ("🌦️", "Drizzle"),
        53: ("🌦️", "Drizzle"),
        55: ("🌦️", "Drizzle"),
        56: ("🌧️", "Freezing drizzle"),
        57: ("🌧️", "Freezing drizzle"),
        61: ("🌧️", "Rain"),
        63: ("🌧️", "Rain"),
        65: ("🌧️", "Rain"),
        66: ("🌨️", "Freezing rain"),
        67: ("🌨️", "Freezing rain"),
        71: ("❄️", "Snow"),
        73: ("❄️", "Snow"),
        75: ("❄️", "Snow"),
        77: ("🌨️", "Snow grains"),
        80: ("🌧️", "Rain showers"),
        81: ("🌧️", "Rain showers"),
        82: ("🌧️", "Rain showers"),
        85: ("❄️", "Snow showers"),
        86: ("❄️", "Snow showers"),
        95: ("⛈️", "Thunderstorm"),
        96: ("⛈️", "Thunderstorm with hail"),
        99: ("⛈️", "Thunderstorm with hail"),
    }
    return mapping.get(code, ("🌈", "Unknown"))

def fetch_weather_data(lat, lon):
    """Fetch current, hourly, and daily weather from Open-Meteo"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "temperature_2m,weathercode,windspeed_10m,relativehumidity_2m",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Weather API error: {str(e)}")

def geocode_city(city_name):
    """Get coordinates and location name from city name"""
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
        return None, None, None
    except Exception:
        return None, None, None

def reverse_geocode(lat, lon):
    """Get location name from coordinates using Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {"User-Agent": "WeatherWise-App/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if "address" in data:
            addr = data["address"]
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("state") or "Unknown"
            country = addr.get("country", "")
            return f"{city}, {country}" if country else city
        return f"Lat: {lat:.2f}, Lon: {lon:.2f}"
    except Exception:
        return f"Coordinates ({lat:.2f}, {lon:.2f})"

def get_location_from_ip():
    """Get location from IP address using ip-api.com"""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=10)
        data = response.json()
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city")
            country = data.get("country")
            location_name = f"{city}, {country}" if city else "Unknown Location"
            return lat, lon, location_name
        return None, None, None
    except Exception:
        return None, None, None

# ---------- Flask Routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather')
def weather():
    """Get weather data for given coordinates"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon parameters"}), 400
    
    try:
        lat = float(lat)
        lon = float(lon)
        data = fetch_weather_data(lat, lon)
        
        # Parse current weather
        current = data.get("current_weather", {})
        temp_c = current.get("temperature")
        wind_kmh = current.get("windspeed")
        weather_code = current.get("weathercode")
        icon_emoji, condition = get_weather_icon(weather_code)
        
        # Get humidity from hourly data (closest hour)
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        humidities = hourly.get("relativehumidity_2m", [])
        humidity = None
        if times and humidities:
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            for i, t in enumerate(times):
                try:
                    t_dt = datetime.fromisoformat(t)
                    if t_dt >= now:
                        humidity = humidities[i] if i < len(humidities) else None
                        break
                except:
                    continue
        
        # Parse hourly data (next 24 hours)
        hourly_list = []
        if times:
            start_idx = 0
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            for i, t in enumerate(times):
                try:
                    if datetime.fromisoformat(t) >= now:
                        start_idx = i
                        break
                except:
                    continue
            # Get up to 24 hours
            for i in range(start_idx, min(start_idx + 24, len(times))):
                try:
                    dt_obj = datetime.fromisoformat(times[i])
                    time_str = dt_obj.strftime("%H:%M")
                except:
                    time_str = times[i][11:16] if len(times[i]) > 11 else times[i]
                hourly_list.append({
                    "time": time_str,
                    "temp": hourly["temperature_2m"][i] if i < len(hourly.get("temperature_2m", [])) else None,
                    "wind": hourly["windspeed_10m"][i] if i < len(hourly.get("windspeed_10m", [])) else None,
                    "weathercode": hourly["weathercode"][i] if i < len(hourly.get("weathercode", [])) else 0,
                })
        
        # Parse daily data
        daily = data.get("daily", {})
        daily_list = []
        days = daily.get("time", [])
        for i in range(min(7, len(days))):
            try:
                dt_obj = datetime.fromisoformat(days[i])
                day_name = dt_obj.strftime("%a")
                date_str = dt_obj.strftime("%d/%m")
            except:
                day_name = days[i][:10]
                date_str = ""
            daily_list.append({
                "day": day_name,
                "date": date_str,
                "max_temp": daily["temperature_2m_max"][i] if i < len(daily.get("temperature_2m_max", [])) else None,
                "min_temp": daily["temperature_2m_min"][i] if i < len(daily.get("temperature_2m_min", [])) else None,
                "wind": daily["windspeed_10m_max"][i] if i < len(daily.get("windspeed_10m_max", [])) else None,
                "weathercode": daily["weathercode"][i] if i < len(daily.get("weathercode", [])) else 0,
            })
        
        return jsonify({
            "current": {
                "temp_c": temp_c,
                "wind_kmh": wind_kmh,
                "weathercode": weather_code,
                "humidity": humidity,
                "condition": condition,
                "icon": icon_emoji,
                "feels_like_c": temp_c,  # Simple approximation
            },
            "hourly": hourly_list,
            "daily": daily_list,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search')
def search():
    """Search city and return coordinates"""
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "Missing city parameter"}), 400
    
    lat, lon, location_name = geocode_city(city)
    if lat is None:
        return jsonify({"error": "City not found"}), 404
    
    return jsonify({
        "lat": lat,
        "lon": lon,
        "name": location_name
    })

@app.route('/api/ip-location')
def ip_location():
    """Get location from IP address"""
    lat, lon, name = get_location_from_ip()
    if lat is None:
        return jsonify({"error": "Could not detect location from IP"}), 500
    return jsonify({
        "lat": lat,
        "lon": lon,
        "name": name
    })

@app.route('/api/reverse-geocode')
def reverse_geocode_route():
    """Get location name from coordinates"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400
    try:
        lat = float(lat)
        lon = float(lon)
        name = reverse_geocode(lat, lon)
        return jsonify({"name": name})
    except Exception:
        return jsonify({"name": f"Location ({lat}, {lon})"})

if __name__ == '__main__':
    app.run(debug=True)