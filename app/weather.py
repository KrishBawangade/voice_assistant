import requests
import json
from typing import Dict, Any
from langchain_core.tools import tool
from app import config

def fetch_weather_data(city: str) -> Dict[str, Any]:
    """
    Helper function to get weather details.
    """
    if not city:
        city = "your current location"

    cleaned_city = city.strip().title()

    if config.OPENWEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={cleaned_city}&appid={config.OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = round(data["main"]["temp"])
                humidity = data["main"]["humidity"]
                wind = round(data["wind"]["speed"] * 3.6)  # Convert m/s to km/h
                condition = data["weather"][0]["main"]
                desc = data["weather"][0]["description"].capitalize()
                
                icon_code = data["weather"][0].get("icon", "01d")
                
                # Standard OpenWeatherMap Icon Mapping to FontAwesome classes
                icon_mapping = {
                    "01d": "sun",
                    "01n": "moon",
                    "02d": "cloud-sun",
                    "02n": "cloud-moon",
                    "03d": "cloud",
                    "03n": "cloud",
                    "04d": "cloud",
                    "04n": "cloud",
                    "09d": "cloud-showers-heavy",
                    "09n": "cloud-showers-heavy",
                    "10d": "cloud-rain",
                    "10n": "cloud-rain",
                    "11d": "bolt",
                    "11n": "bolt",
                    "13d": "snowflake",
                    "13n": "snowflake",
                    "50d": "smog",
                    "50n": "smog"
                }
                icon = icon_mapping.get(icon_code, "sun")

                return {
                    "city": cleaned_city,
                    "temperature": f"{temp}°C",
                    "condition": condition,
                    "description": desc,
                    "humidity": f"{humidity}%",
                    "wind": f"{wind} km/h",
                    "icon": icon,
                    "simulated": False
                }
        except Exception:
            pass  # Fall back to simulation

    # Simulation mode (Celsius based)
    city_hash = sum(ord(c) for c in cleaned_city)
    conditions = [
        {"cond": "Sunny", "desc": "Clear skies and delightful breeze", "icon": "sun", "base_temp": 25, "humidity": 45, "wind": 10},
        {"cond": "Partly Cloudy", "desc": "Scattered clouds with sunshine", "icon": "cloud-sun", "base_temp": 20, "humidity": 55, "wind": 12},
        {"cond": "Overcast", "desc": "Gloomy grey skies", "icon": "cloud", "base_temp": 15, "humidity": 70, "wind": 15},
        {"cond": "Rainy", "desc": "Light to moderate showers", "icon": "cloud-showers-heavy", "base_temp": 12, "humidity": 85, "wind": 18},
        {"cond": "Stormy", "desc": "Heavy thunder and lightning storm", "icon": "bolt", "base_temp": 18, "humidity": 90, "wind": 30},
        {"cond": "Chilly", "desc": "Crisp air with clear views", "icon": "snowflake", "base_temp": 3, "humidity": 30, "wind": 22},
    ]
    
    weather_type = conditions[city_hash % len(conditions)]
    temp_variance = (len(cleaned_city) % 9) - 4
    final_temp = weather_type["base_temp"] + temp_variance
    final_wind = weather_type["wind"] + (city_hash % 5)
    final_humidity = min(100, max(10, weather_type["humidity"] + (city_hash % 11) - 5))

    return {
        "city": cleaned_city,
        "temperature": f"{final_temp}°C",
        "condition": weather_type["cond"],
        "description": weather_type["desc"],
        "humidity": f"{final_humidity}%",
        "wind": f"{final_wind} km/h",
        "icon": weather_type["icon"],
        "simulated": True
    }

@tool
def get_current_weather(city: str) -> str:
    """
    Fetches the current weather report and forecast for a given city name.
    Use this tool whenever the user asks for the weather, temperature, or forecast in a specific city.
    """
    data = fetch_weather_data(city)
    return json.dumps(data)
