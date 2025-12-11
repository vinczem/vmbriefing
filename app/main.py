import json
import time
import threading
import os
from flask import Flask, render_template
from rss_fetcher import RSSFetcher
from weather_fetcher import WeatherFetcher
from ai_summarizer import AISummarizer
from ha_client import HAClient

app = Flask(__name__)
latest_briefing = "Waiting for first update..."
last_updated = "Never"
data_store = {
    "news_items": [],
    "ai_summary": None,
    "weather_summary": "Betöltés...",
    "avg_temp_text": "",
    "current_date": "",
    "last_updated": "Never"
}

def load_config():
    try:
        with open("/data/options.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: /data/options.json not found, returning empty config")
        return {}

def generate_briefing():
    global latest_briefing, last_updated
    print("Starting briefing generation...")
    
    config = load_config()
    print(f"DEBUG: Loaded config keys: {list(config.keys())}")
    print(f"DEBUG: Selected Provider: {config.get('ai_provider')}")
    print(f"DEBUG: Gemini Key Present? {bool(config.get('gemini_api_key'))}")
    
    # 1. RSS News
    rss = RSSFetcher(config.get("rss_feeds", []), config.get("news_hours", 24))
    news_items = rss.fetch_news()
    
    news_text = ""
    news_text = ""
    ai_provider = config.get("ai_provider", "openai")
    
    # Check for credentials based on provider
    api_key = None
    model = None
    
    if ai_provider == "openai":
        api_key = config.get("openai_api_key")
        model = config.get("openai_model", "gpt-3.5-turbo")
    elif ai_provider == "gemini":
        api_key = config.get("gemini_api_key")
        model = config.get("gemini_model", "gemini-1.5-flash")
    
    if api_key:
        print(f"Using AI Summarizer ({ai_provider})...")
        import datetime
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        ai = AISummarizer(ai_provider, api_key, model)
        
        # Retry logic for AI summarization
        summary = None
        max_retries = 3
        retry_delay = 10
        
        # Determine part of day for greeting
        current_hour = datetime.datetime.now().hour
        part_of_day = "napközben"
        if 5 <= current_hour < 10:
            part_of_day = "reggel"
        elif 10 <= current_hour < 18:
            part_of_day = "napközben"
        elif current_hour >= 18 or current_hour < 5:
            part_of_day = "este"
            
        for attempt in range(max_retries):
            print(f"Generating AI summary (attempt {attempt + 1}/{max_retries})...")
            summary = ai.summarize(news_items, current_date=today, part_of_day=part_of_day)
            if summary:
                break
            
            if attempt < max_retries - 1:
                print(f"AI generation failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        
        if summary:
            news_text = f"A legfontosabb hírek:\n{summary}"
        else:
            news_text = "Hiba történt az AI összefoglaló generálásakor. (Lásd logok)"
    else:
        print(f"No API key found for provider {ai_provider}. Fallback to list.")
        # Fallback to simple list
        if news_items:
            news_text = "Legfontosabb hírek:\n"
            for item in news_items:
                news_text += f"- {item['title']}\n"
        else:
            news_text = "Nincsenek friss hírek.\n"

    # 2. Weather
    weather = WeatherFetcher(
        config.get("weather_api_key"),
        config.get("weather_lat"),
        config.get("weather_lon")
    )
    weather_text = weather.fetch_forecast()

    # 3. Home Temp
    ha = HAClient()
    avg_temp = ha.get_avg_temperature(config.get("temp_sensors", []))
    temp_text = ""
    if avg_temp is not None:
        temp_text = f"A lakás átlagos hőmérséklete: {avg_temp:.1f}°C."
    else:
        temp_text = "A lakás hőmérséklete nem elérhető."

    # Combine (Keep for legacy/debugging)
    briefing = f"{weather_text}\n{temp_text}\n\n{news_text}"
    
    latest_briefing = briefing
    last_updated = time.ctime()
    
    # Update Data Store for Template
    import datetime
    global data_store
    data_store = {
        "news_items": news_items,
        "ai_summary": summary if 'summary' in locals() and summary else news_text, # Fallback to list text if no summary object
        "weather_summary": weather_text,
        "avg_temp_text": temp_text,
        "current_date": datetime.date.today().strftime("%Y. %m. %d."),
        "last_updated": last_updated
    }
    
    # Update HA Entity
    ha.update_state("sensor.vmbriefing_text", "OK", {
        "briefing_text": briefing,
        "last_updated": last_updated
    })
    print("Briefing generated and updated.")

def scheduler_loop():
    while True:
        try:
            generate_briefing()
        except Exception as e:
            print(f"Error in generation loop: {e}")
            
        config = load_config()
        interval = config.get("update_interval", 60) * 60
        time.sleep(interval)

@app.route("/")
def index():
    return render_template("index.html", **data_store)

# Start scheduler in background when imported (Gunicorn)
# Ensure it only runs once if multiple imports happen (basic check)
if not any(t.name == "BriefingScheduler" for t in threading.enumerate()):
    t = threading.Thread(target=scheduler_loop, daemon=True, name="BriefingScheduler")
    t.start()

if __name__ == "__main__":
    # Start Web UI (Dev mode only)
    app.run(host="0.0.0.0", port=5000)
