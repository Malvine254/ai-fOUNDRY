import requests

API_KEY = "67d16b9607ee0b8eefcb9f4dfa7ca884"
CITY = "Nairobi"

url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    print(f"✅ Weather in {CITY}")
    print(f"Description: {data['weather'][0]['description'].capitalize()}")
    print(f"Temperature: {data['main']['temp']}°C")
    print(f"Feels like: {data['main']['feels_like']}°C")
    print(f"Humidity: {data['main']['humidity']}%")
    print(f"Wind Speed: {data['wind']['speed']} m/s")
else:
    print(f"❌ Error fetching weather: {data.get('message', 'Unknown error')}")
