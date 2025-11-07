import os
import requests

def get_weather(city=None, lat=None, lon=None):
    """
    Fetch current weather data from OpenWeatherMap.
    Returns clean, Bootstrap-ready HTML for the assistant UI.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "<p>❌ Weather API key not configured. Set OPENWEATHER_API_KEY in .env.</p>"

    # Decide API URL
    if lat and lon:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    elif city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    else:
        # fallback default
        default_city = os.getenv("DEFAULT_CITY", "Nairobi")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={default_city}&appid={api_key}&units=metric"

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if resp.status_code != 200 or "weather" not in data:
            msg = data.get("message", "Unable to fetch weather data.")
            return f"<p>⚠️ Could not retrieve weather: {msg.capitalize()}.</p>"

        # Extract values safely
        city_name = data.get("name") or city or "Unknown location"
        desc = data["weather"][0]["description"].capitalize()
        icon = data["weather"][0].get("icon", "")
        temp = data["main"].get("temp", "?")
        feels_like = data["main"].get("feels_like", "?")
        humidity = data["main"].get("humidity", "?")
        wind = data["wind"].get("speed", "?")

        # Pick a nice emoji
        emoji = "🌤"
        if "rain" in desc.lower():
            emoji = "🌧"
        elif "cloud" in desc.lower():
            emoji = "☁️"
        elif "clear" in desc.lower():
            emoji = "☀️"
        elif "storm" in desc.lower():
            emoji = "⛈"
        elif "snow" in desc.lower():
            emoji = "❄️"

        html = f"""
        <div class="card p-3 bg-light border mt-2 weather-card">
            <h5 class="fw-bold mb-2">{emoji} Weather in {city_name}</h5>
            <ul class="mb-0 ps-3">
                <li><b>Condition:</b> {desc}</li>
                <li><b>Temperature:</b> {temp}°C (feels like {feels_like}°C)</li>
                <li><b>Humidity:</b> {humidity}%</li>
                <li><b>Wind Speed:</b> {wind} m/s</li>
            </ul>
        </div>
        """
        return html.strip()

    except requests.exceptions.Timeout:
        return "<p>⏱️ Weather request timed out. Please try again.</p>"
    except Exception as e:
        return f"<p>⚠️ Weather lookup failed: {str(e)}</p>"
