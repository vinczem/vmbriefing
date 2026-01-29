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
            import datetime
            
            # 1. Fetch Forecast (5 day / 3 hour)
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=metric&lang=hu"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # --- Current Weather (First item in list serves as proxy for "now" or use separate 'weather' endpoint if needed, 
            # but 'forecast' list[0] is usually close enough for a general briefing - usually within 1.5 hours) ---
            current = data['list'][0]
            curr_desc = current['weather'][0]['description']
            curr_temp = current['main']['temp']
            
            text = f"Időjárás: Jelenleg {curr_desc}, {curr_temp:.1f}°C."

            # --- Future Forecast Logic ---
            now = datetime.datetime.now()
            target_hour = 14 # Default: Afternoon
            target_label = "délután"
            
            # Logic:
            # - Morning (00-09): Target 14:00 (Today Afternoon)
            # - Day (10-17): Target 20:00 (Today Evening)
            # - Evening (18-23): Target 08:00 (Tomorrow Morning)
            
            if 0 <= now.hour < 10:
                target_hour = 14
                target_label = "délután"
                target_date = now.date()
            elif 10 <= now.hour < 18:
                target_hour = 20
                target_label = "este"
                target_date = now.date()
            else: # 18 <= now.hour <= 23
                target_hour = 8
                target_label = "holnap reggel"
                target_date = now.date() + datetime.timedelta(days=1)
                
            # Find the forecast item closest to target_date + target_hour
            best_item = None
            min_diff = float('inf')
            
            for item in data['list']:
                # item['dt'] is unix timestamp
                item_dt = datetime.datetime.fromtimestamp(item['dt'])
                
                # We only care if it matches the target date (approx) and is in the future relative to now?
                # actually just searching for the specific timestamp closest to our target
                target_dt = datetime.datetime.combine(target_date, datetime.time(target_hour, 0))
                
                diff = abs((item_dt - target_dt).total_seconds())
                
                if diff < min_diff:
                    min_diff = diff
                    best_item = item
            
            if best_item:
                fut_desc = best_item['weather'][0]['description']
                fut_temp = best_item['main']['temp']
                text += f" Várhatóan {target_label}: {fut_desc}, {fut_temp:.1f}°C."
            
            return text
            
        except Exception as e:
            return f"Error fetching weather: {e}"
