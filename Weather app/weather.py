import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime
import os
import sys

# -------------------------------
# Weather icon mapping (Open-Meteo WMO codes)
# -------------------------------
def get_weather_icon(code):
    """Return emoji and description for WMO weather code"""
    if code == 0:
        return "☀️", "Clear sky"
    elif code in (1, 2):
        return "🌤️", "Mainly clear"
    elif code == 3:
        return "☁️", "Overcast"
    elif code in (45, 48):
        return "🌫️", "Fog"
    elif code in (51, 53, 55):
        return "🌦️", "Drizzle"
    elif code in (56, 57):
        return "🌧️", "Freezing drizzle"
    elif code in (61, 63, 65):
        return "🌧️", "Rain"
    elif code in (66, 67):
        return "🌨️", "Freezing rain"
    elif code in (71, 73, 75):
        return "❄️", "Snow"
    elif code == 77:
        return "🌨️", "Snow grains"
    elif code in (80, 81, 82):
        return "🌧️", "Rain showers"
    elif code in (85, 86):
        return "❄️", "Snow showers"
    elif code == 95:
        return "⛈️", "Thunderstorm"
    elif code in (96, 99):
        return "⛈️", "Thunderstorm with hail"
    else:
        return "🌈", "Unknown"

# -------------------------------
# Geolocation (IP-based)
# -------------------------------
def get_location_from_ip():
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
        else:
            return None, None, None
    except Exception:
        return None, None, None

# -------------------------------
# Geocoding (city name to coordinates)
# -------------------------------
def geocode_city(city_name):
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
        else:
            return None, None, None
    except Exception:
        return None, None, None

# -------------------------------
# Fetch weather data from Open-Meteo
# -------------------------------
def fetch_weather_data(lat, lon):
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
        data = response.json()
        return data
    except Exception as e:
        raise Exception(f"Weather API error: {str(e)}")

# -------------------------------
# Main Application Class
# -------------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WeatherWise - Graphical Weather App")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set background color for the whole window
        self.root.configure(bg="#2B2949")
        
        # ---------- RELIABLE CUSTOM ICON (works in .exe) ----------
        import os
        import sys

        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.custom_icon = None
        try:
            # Use PNG + iconphoto (cross-platform, needs Pillow)
            from PIL import Image, ImageTk
            png_path = resource_path("favicon.png")   # <-- your PNG file
            if os.path.exists(png_path):
                img = Image.open(png_path).resize((32, 32), Image.LANCZOS)
                self.custom_icon = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self.custom_icon)
                print("PNG icon loaded")
            else:
                print(f"PNG not found at {png_path}")
        except Exception as e:
            print(f"iconphoto failed: {e}")
            # Fallback: try .ico for Windows
            try:
                ico_path = resource_path("favicon.ico")
                self.root.iconbitmap(ico_path)
                print("ICO icon loaded")
            except Exception as e2:
                print(f"ICO also failed: {e2}")
        # ---------------------------------------------------------
        
        # Stored data
        self.weather_raw = None
        self.current_location = "Unknown"
        self.current_lat = None
        self.current_lon = None
        self.temp_unit = "C"
        self.wind_unit = "kmh"
        
        # Apply custom styling
        self._setup_styles()
        
        # Build UI
        self._build_ui()
        
        # Auto-detect location
        self.auto_detect_location()
    
    def _setup_styles(self):
        """Modern styling for the entire app"""
        style = ttk.Style()
        
        # Available themes: 'clam', 'alt', 'default', 'vista', 'xpnative'
        # Use 'clam' for better customization
        style.theme_use('clam')
        
        # Configure colors
        bg_color = "#1C2A33"
        fg_color = "#ffffff"
        accent_color = "#4a90e2"
        card_bg = "#151620"
        button_bg = "#4a90e2"
        button_fg = "#ffffff"
        
        # Root background
        self.root.configure(bg=bg_color)
        
        # General ttk styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TLabelframe", background=bg_color, foreground=fg_color, bordercolor=accent_color, relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=bg_color, foreground=accent_color, font=("Segoe UI", 10, "bold"))
        
        # Custom label styles
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=accent_color, background=bg_color)
        style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"), foreground="#ffffff", background=bg_color)
        style.configure("Weather.TLabel", font=("Segoe UI", 12), foreground="#dddddd", background=bg_color)
        style.configure("Temp.TLabel", font=("Segoe UI", 36, "bold"), foreground="#ffffff", background=bg_color)
        style.configure("Info.TLabel", font=("Segoe UI", 10), foreground="#aaaaaa", background=bg_color)
        
        # Buttons
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), background=button_bg, foreground=button_fg, borderwidth=0, focusthickness=0, padding=6)
        style.map("Accent.TButton",
                  background=[('active', '#5da0e8'), ('pressed', '#3a7bc8')],
                  foreground=[('active', 'white')])
        
        # Entry widget
        style.configure("TEntry", fieldbackground="#3a3a4f", foreground="white", borderwidth=0, focuscolor=accent_color)
        style.map("TEntry", fieldbackground=[('focus', '#3a3a4f')])
        
        # Notebook (tabs)
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#2a2a3b", foreground="#cccccc", padding=[12, 4], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[('selected', accent_color), ('active', '#4a5a7a')],
                  foreground=[('selected', 'white'), ('active', 'white')])
        
        # Scrollbar
        style.configure("Horizontal.TScrollbar", background=accent_color, troughcolor="#2a2a3b", borderwidth=0)
        
        # Cards for hourly/daily
        style.configure("Card.TFrame", background=card_bg, relief="solid", borderwidth=1, bordercolor="#3a3a4f")
        style.configure("Card.TLabel", background=card_bg, foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=card_bg, foreground=accent_color, font=("Segoe UI", 11, "bold"))
    
    def _build_ui(self):
        # Main container frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ----- Top Control Panel -----
        control_frame = ttk.LabelFrame(main_frame, text="📍 Location & Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0,15))
        
        # Location row
        loc_frame = ttk.Frame(control_frame)
        loc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(loc_frame, text="City:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0,10))
        self.city_entry = ttk.Entry(loc_frame, width=30, font=("Segoe UI", 11))
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind("<Return>", lambda e: self.search_location())
        
        self.search_btn = ttk.Button(loc_frame, text="🔍 Search", command=self.search_location, style="Accent.TButton")
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.auto_btn = ttk.Button(loc_frame, text="📍 Auto Detect", command=self.auto_detect_location, style="Accent.TButton")
        self.auto_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(loc_frame, text="⟳ Refresh", command=self.refresh_weather, style="Accent.TButton")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Unit selection row
        unit_frame = ttk.Frame(control_frame)
        unit_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Label(unit_frame, text="Units:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0,15))
        
        self.temp_unit_var = tk.StringVar(value="C")
        ttk.Radiobutton(unit_frame, text="°Celsius", variable=self.temp_unit_var, value="C", command=self._on_unit_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(unit_frame, text="°Fahrenheit", variable=self.temp_unit_var, value="F", command=self._on_unit_change).pack(side=tk.LEFT, padx=15)
        
        self.wind_unit_var = tk.StringVar(value="kmh")
        ttk.Radiobutton(unit_frame, text="km/h", variable=self.wind_unit_var, value="kmh", command=self._on_unit_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(unit_frame, text="mph", variable=self.wind_unit_var, value="mph", command=self._on_unit_change).pack(side=tk.LEFT, padx=15)
        
        # Status label
        self.status_var = tk.StringVar(value="✨ Ready. Auto-detecting location...")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, font=("Segoe UI", 9, "italic"), foreground="#aaaaaa")
        status_label.pack(fill=tk.X, pady=(10,0))
        
        # ----- Notebook Tabs -----
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Current Conditions Tab
        self.current_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.current_frame, text=" 🌡️ Current ")
        
        # Hourly Tab
        self.hourly_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.hourly_frame, text=" ⏱️ Hourly (12h) ")
        
        # Daily Tab
        self.daily_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.daily_frame, text=" 📅 7-Day Forecast ")
        
        # Build sub-sections
        self._build_current_tab()
        self._build_hourly_tab()
        self._build_daily_tab()
        
        # Show loading placeholders
        self._show_loading()
    
    def _build_current_tab(self):
        # Location and time
        self.location_label = ttk.Label(self.current_frame, text="Location: --", style="Title.TLabel")
        self.location_label.pack(anchor=tk.W, pady=(0,5))
        
        self.update_time_label = ttk.Label(self.current_frame, text="Last update: --", style="Info.TLabel")
        self.update_time_label.pack(anchor=tk.W, pady=(0,20))
        
        # Main weather card
        weather_card = ttk.Frame(self.current_frame, style="Card.TFrame")
        weather_card.pack(fill=tk.X, pady=10, padx=10)
        
        # Icon and temperature side by side
        icon_temp_frame = ttk.Frame(weather_card, style="Card.TFrame")
        icon_temp_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.icon_label = ttk.Label(icon_temp_frame, text="🌈", font=("Segoe UI", 72), style="Card.TLabel")
        self.icon_label.pack(side=tk.LEFT, padx=(0,30))
        
        temp_frame = ttk.Frame(icon_temp_frame, style="Card.TFrame")
        temp_frame.pack(side=tk.LEFT)
        
        self.temp_label = ttk.Label(temp_frame, text="--°C", style="Temp.TLabel")
        self.temp_label.pack(anchor=tk.W)
        
        self.condition_label = ttk.Label(temp_frame, text="--", style="Heading.TLabel")
        self.condition_label.pack(anchor=tk.W)
        
        # Additional details in a grid
        details_frame = ttk.LabelFrame(self.current_frame, text="Details", padding="15")
        details_frame.pack(fill=tk.X, pady=15, padx=10)
        
        self.wind_label = ttk.Label(details_frame, text="💨 Wind: --", style="Weather.TLabel")
        self.wind_label.grid(row=0, column=0, sticky=tk.W, pady=8, padx=15)
        
        self.humidity_label = ttk.Label(details_frame, text="💧 Humidity: --", style="Weather.TLabel")
        self.humidity_label.grid(row=0, column=1, sticky=tk.W, pady=8, padx=15)
        
        self.feels_label = ttk.Label(details_frame, text="🌡️ Feels like: --", style="Weather.TLabel")
        self.feels_label.grid(row=1, column=0, sticky=tk.W, pady=8, padx=15)
        
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)
    
    def _build_hourly_tab(self):
        # Horizontal scrollable canvas
        self.hourly_canvas = tk.Canvas(self.hourly_frame, highlightthickness=0, bg="#1e1e2f")
        scrollbar = ttk.Scrollbar(self.hourly_frame, orient="horizontal", command=self.hourly_canvas.xview)
        self.hourly_canvas.configure(xscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hourly_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.hourly_inner = ttk.Frame(self.hourly_canvas)
        self.hourly_canvas.create_window((0,0), window=self.hourly_inner, anchor="nw")
        self.hourly_inner.bind("<Configure>", lambda e: self.hourly_canvas.configure(scrollregion=self.hourly_canvas.bbox("all")))
    
    def _build_daily_tab(self):
        self.daily_container = ttk.Frame(self.daily_frame)
        self.daily_container.pack(fill=tk.BOTH, expand=True)
    
    def _show_loading(self):
        self.location_label.config(text="Location: Loading...")
        self.temp_label.config(text="--")
        self.condition_label.config(text="Fetching data...")
        self.wind_label.config(text="💨 Wind: --")
        self.humidity_label.config(text="💧 Humidity: --")
        self.feels_label.config(text="🌡️ Feels like: --")
        
        for widget in self.hourly_inner.winfo_children():
            widget.destroy()
        for widget in self.daily_container.winfo_children():
            widget.destroy()
    
    def _on_unit_change(self):
        self.temp_unit = self.temp_unit_var.get()
        self.wind_unit = self.wind_unit_var.get()
        if self.weather_raw:
            self._refresh_display_from_stored()
    
    def _refresh_display_from_stored(self):
        if self.weather_raw:
            self._update_current_tab()
            self._update_hourly_tab()
            self._update_daily_tab()
    
    def _convert_temp(self, celsius):
        if self.temp_unit == "C":
            return celsius, "°C"
        else:
            return celsius * 9/5 + 32, "°F"
    
    def _convert_wind(self, kmh):
        if self.wind_unit == "kmh":
            return kmh, "km/h"
        else:
            return kmh * 0.621371, "mph"
    
    def _update_current_tab(self):
        if not self.weather_raw:
            return
        current = self.weather_raw.get("current_weather", {})
        if not current:
            return
        
        temp_c = current.get("temperature")
        wind_kmh = current.get("windspeed")
        weather_code = current.get("weathercode")
        icon, condition = get_weather_icon(weather_code)
        
        temp_val, temp_unit = self._convert_temp(temp_c)
        wind_val, wind_unit = self._convert_wind(wind_kmh)
        
        self.icon_label.config(text=icon)
        self.temp_label.config(text=f"{temp_val:.1f}{temp_unit}")
        self.condition_label.config(text=condition)
        self.wind_label.config(text=f"💨 Wind: {wind_val:.1f} {wind_unit}")
        
        # Humidity extraction
        hourly = self.weather_raw.get("hourly", {})
        times = hourly.get("time", [])
        humidities = hourly.get("relativehumidity_2m", [])
        humidity_str = "--"
        if times and humidities:
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            for i, t in enumerate(times):
                try:
                    t_dt = datetime.fromisoformat(t)
                    if t_dt >= now:
                        humidity_str = f"{humidities[i]}%"
                        break
                except:
                    continue
        self.humidity_label.config(text=f"💧 Humidity: {humidity_str}")
        self.feels_label.config(text=f"🌡️ Feels like: {temp_val:.1f}{temp_unit}")
        self.location_label.config(text=f"📍 {self.current_location}")
        self.update_time_label.config(text=f"🕒 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _update_hourly_tab(self):
        for widget in self.hourly_inner.winfo_children():
            widget.destroy()
        
        hourly = self.weather_raw.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        winds = hourly.get("windspeed_10m", [])
        codes = hourly.get("weathercode", [])
        
        if not times:
            ttk.Label(self.hourly_inner, text="No hourly data", style="Weather.TLabel").pack()
            return
        
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        start_idx = 0
        for i, t_str in enumerate(times):
            try:
                t_dt = datetime.fromisoformat(t_str)
                if t_dt >= now:
                    start_idx = i
                    break
            except:
                continue
        
        end_idx = min(start_idx + 12, len(times))
        for i in range(start_idx, end_idx):
            time_str = times[i]
            try:
                dt = datetime.fromisoformat(time_str)
                hour_label = dt.strftime("%H:%M")
            except:
                hour_label = time_str[11:16] if len(time_str) > 11 else time_str
            
            temp_c = temps[i] if i < len(temps) else None
            wind_kmh = winds[i] if i < len(winds) else None
            code = codes[i] if i < len(codes) else 0
            icon, _ = get_weather_icon(code)
            
            temp_val, temp_unit = self._convert_temp(temp_c) if temp_c is not None else (None, "")
            wind_val, wind_unit = self._convert_wind(wind_kmh) if wind_kmh is not None else (None, "")
            
            card = ttk.Frame(self.hourly_inner, style="Card.TFrame", padding=10)
            card.pack(side=tk.LEFT, padx=6, pady=8, fill=tk.Y)
            
            ttk.Label(card, text=hour_label, style="CardTitle.TLabel").pack()
            ttk.Label(card, text=icon, font=("Segoe UI", 28), style="Card.TLabel").pack(pady=5)
            if temp_val is not None:
                ttk.Label(card, text=f"{temp_val:.1f}{temp_unit}", style="Card.TLabel").pack()
            if wind_val is not None:
                ttk.Label(card, text=f"{wind_val:.1f}{wind_unit}", style="Card.TLabel", foreground="#aaaaaa").pack()
    
    def _update_daily_tab(self):
        for widget in self.daily_container.winfo_children():
            widget.destroy()
        
        daily = self.weather_raw.get("daily", {})
        days = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        winds = daily.get("windspeed_10m_max", [])
        codes = daily.get("weathercode", [])
        
        if not days:
            ttk.Label(self.daily_container, text="No daily forecast", style="Weather.TLabel").pack()
            return
        
        for idx in range(min(len(days), 7)):
            day_str = days[idx]
            try:
                dt = datetime.fromisoformat(day_str)
                day_name = dt.strftime("%A")[:3]
                date_str = dt.strftime("%d/%m")
            except:
                day_name = day_str[:10]
                date_str = ""
            
            max_c = max_temps[idx] if idx < len(max_temps) else None
            min_c = min_temps[idx] if idx < len(min_temps) else None
            wind_kmh = winds[idx] if idx < len(winds) else None
            code = codes[idx] if idx < len(codes) else 0
            icon, _ = get_weather_icon(code)
            
            max_val, max_unit = self._convert_temp(max_c) if max_c is not None else (None, "")
            min_val, min_unit = self._convert_temp(min_c) if min_c is not None else (None, "")
            wind_val, wind_unit = self._convert_wind(wind_kmh) if wind_kmh is not None else (None, "")
            
            card = ttk.Frame(self.daily_container, style="Card.TFrame", padding=12, width=150)
            card.grid(row=0, column=idx, padx=8, pady=6, sticky=tk.N)
            card.grid_propagate(False)
            
            ttk.Label(card, text=day_name, style="CardTitle.TLabel").pack()
            ttk.Label(card, text=date_str, style="Card.TLabel", foreground="#aaaaaa").pack()
            ttk.Label(card, text=icon, font=("Segoe UI", 36), style="Card.TLabel").pack(pady=5)
            
            if max_val is not None and min_val is not None:
                ttk.Label(card, text=f"↑ {max_val:.1f}{max_unit}", style="Card.TLabel", foreground="#ff6b6b").pack()
                ttk.Label(card, text=f"↓ {min_val:.1f}{min_unit}", style="Card.TLabel", foreground="#6bc5ff").pack()
            if wind_val is not None:
                ttk.Label(card, text=f"💨 {wind_val:.1f}{wind_unit}", style="Card.TLabel", foreground="#aaaaaa").pack()
    
    # --- Networking & threading methods (unchanged from original) ---
    def _fetch_and_display(self, lat, lon, location_name):
        try:
            self.root.after(0, lambda: self.status_var.set(f"Fetching weather for {location_name}..."))
            data = fetch_weather_data(lat, lon)
            self.weather_raw = data
            self.current_lat = lat
            self.current_lon = lon
            self.current_location = location_name
            self.root.after(0, self._on_fetch_success)
        except Exception as e:
            self.root.after(0, lambda: self._on_fetch_error(str(e)))
    
    def _on_fetch_success(self):
        self._refresh_display_from_stored()
        self.status_var.set(f"✅ Updated: {self.current_location}")
        self._set_buttons_state(True)
    
    def _on_fetch_error(self, error_msg):
        messagebox.showerror("Error", f"Failed to get weather data:\n{error_msg}")
        self.status_var.set(f"❌ Error: {error_msg}")
        self._set_buttons_state(True)
        self._show_loading()
    
    def _set_buttons_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.search_btn.config(state=state)
        self.auto_btn.config(state=state)
        self.refresh_btn.config(state=state)
    
    def _start_weather_fetch(self, lat, lon, location_name):
        self._set_buttons_state(False)
        self._show_loading()
        thread = threading.Thread(target=self._fetch_and_display, args=(lat, lon, location_name), daemon=True)
        thread.start()
    
    def auto_detect_location(self):
        self.status_var.set("Detecting your location via IP...")
        self._set_buttons_state(False)
        def detect():
            lat, lon, loc_name = get_location_from_ip()
            if lat is None:
                self.root.after(0, lambda: self._on_detect_failed())
            else:
                self.root.after(0, lambda: self._start_weather_fetch(lat, lon, loc_name))
        threading.Thread(target=detect, daemon=True).start()
    
    def _on_detect_failed(self):
        self._set_buttons_state(True)
        messagebox.showerror("Location Error", "Could not detect location automatically.\nPlease enter city manually.")
        self.status_var.set("Auto-detection failed. Enter city name.")
    
    def search_location(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return
        self.status_var.set(f"Searching for '{city}'...")
        self._set_buttons_state(False)
        def geocode_and_fetch():
            lat, lon, loc_name = geocode_city(city)
            if lat is None:
                self.root.after(0, lambda: self._on_search_failed(city))
            else:
                self.root.after(0, lambda: self._start_weather_fetch(lat, lon, loc_name))
        threading.Thread(target=geocode_and_fetch, daemon=True).start()
    
    def _on_search_failed(self, city):
        self._set_buttons_state(True)
        messagebox.showerror("Location Not Found", f"Could not find city: '{city}'\nPlease check spelling or try another.")
        self.status_var.set("Search failed. Try different city name.")
    
    def refresh_weather(self):
        if self.current_lat is not None and self.current_lon is not None:
            self._start_weather_fetch(self.current_lat, self.current_lon, self.current_location)
        else:
            messagebox.showinfo("No Location", "No location data. Use 'Auto Detect' or 'Search' first.")

# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()