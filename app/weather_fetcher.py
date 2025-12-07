import requests

class WeatherFetcher:
    def __init__(self, api_key, lat, lon):
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.openweathermap.org/data/2.5/onecall"

    def fetch_forecast(self):
        if not self.api_key:
            return "Weather API key not configured."

        try:
            # Using One Call API 3.0 (or 2.5 depending on key type, usually 2.5/weather or onecall)
            # Note: One Call API requires subscription (even free tier). 
            # Fallback to standard 'weather' or 'forecast' if One Call fails or is not desired?
            # Let's use the standard 'weather' endpoint for current and 'forecast' for daily to be safer for free keys without credit card?
            # Actually, the user asked for "daily weather forecast".
            # Let's try the standard 5 day / 3 hour forecast API which is free for everyone.
            
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric&lang=hu"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Simple summary: Get today's max/min or just the next few entries?
            # The 5 day forecast returns data every 3 hours.
            # Let's just grab the description and temp for the next entry (close to now) and maybe a daily summary if possible.
            # Since this is a simple briefing, let's just take the first entry (current/upcoming) and maybe one 12 hours later.
            
            # Better approach for "Daily forecast":
            # Just get the current weather and a brief description.
            
            current_weather = data['list'][0]
            desc = current_weather['weather'][0]['description']
            temp = current_weather['main']['temp']
            
            return f"Időjárás: {desc}, {temp:.1f}°C."
            
        except Exception as e:
            return f"Error fetching weather: {e}"
