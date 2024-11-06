from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta, timezone
import requests_cache
from retry_requests import retry
import calendar
import os
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

HISTORY_FILE = '/tmp/search_history.json'

# Define a custom Jinja2 filter for formatting datetime
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    dt = datetime.fromisoformat(value)
    return dt.strftime(format)

def append_to_history(city_name, city_info, forecast_info):
    # Load existing history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    else:
        history = []

    # Append new entry
    history.append({
        "timestamp": datetime.now().isoformat(),
        "city_name": city_name,
        "city_info": city_info,
        "forecast_info": forecast_info
    })

    # Save updated history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Fetch the background color from environment variables
    bg_color = os.getenv('BG_COLOR', '#FFFFFF')  # Default to white if not set

    city_info = None
    forecast_info = None
    
    # Ensure the directory for caching exists within /tmp
    cache_dir = '/tmp/.cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_session = requests_cache.CachedSession(cache_dir, expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

    if request.method == 'POST':
        city_name = request.form['city_name']
        geocoding_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json'
        city_list = retry_session.get(geocoding_url)

        if city_list.status_code == 200:
            data = city_list.json()

            if 'results' in data:
                location = data['results'][0]
                latitude = location['latitude']
                longitude = location['longitude']
                time_zone = location.get('timezone', 'UTC')
                country = location.get('country', 'Unknown')

                city_info = {
                    "name": location['name'],
                    "country": country
                }

                weather_url = "https://api.open-meteo.com/v1/forecast"
                start_date = datetime.now(timezone.utc).date()
                end_date = start_date + timedelta(days=7)
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": time_zone,
                    "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                    "hourly": "relative_humidity_2m",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                response = retry_session.get(weather_url, params=params)

                if response.status_code == 200:
                    forecast_data = response.json()
                    daily_data = forecast_data.get('daily', {})
                    hourly_data = forecast_data.get('hourly', {})
                    forecast_info = []

                    time_list = daily_data.get('time', [])
                    max_temps = daily_data.get('temperature_2m_max', [])
                    min_temps = daily_data.get('temperature_2m_min', [])
                    weather_code = daily_data.get('weather_code', [])
                    humidity = hourly_data.get('relative_humidity_2m', [])
                    humidity_by_day = []

                    for i in range(0, len(humidity), 24):
                        daily_humidity = humidity[i:i+24]
                        avg_humidity = sum(daily_humidity) / len(daily_humidity)
                        humidity_by_day.append(avg_humidity)

                    for i in range(0,len(weather_code)):
                        temp = weather_code[i]
                        if temp <45:
                            weather_code[i] = "clear_sky"
                        elif temp>=45 and temp<61:
                            weather_code[i] = "fog"
                        elif temp>=61 and temp<71:
                            weather_code[i] = "rain"
                        elif temp>=71 and temp<85:
                            weather_code[i] = "snow"
                        else:
                            weather_code[i] = "thunderstorm"

                    for i in range(len(time_list)):
                        date_obj = datetime.strptime(time_list[i], "%Y-%m-%d")
                        day_of_week = calendar.day_name[date_obj.weekday()]
                        forecast_info.append({
                            "date": time_list[i],
                            "max": max_temps[i],
                            "min": min_temps[i],
                            "humidity": humidity_by_day[i],
                            "day_of_week": day_of_week,
                            "weather_code" : weather_code[i]
                        })
                else:
                    forecast_info = {"error": "Could not fetch weather data"}
            else:
                city_info = {"name": "Unknown", "country": "Unknown"}
                forecast_info = {"error": "City not found"}

        # Save the search and forecast info to the history
        append_to_history(city_name, city_info, forecast_info)

    return render_template("index.html", city_info=city_info, forecast_info=forecast_info, bg_color=bg_color)

@app.route('/history', methods=['GET'])
def history():
    # Fetch the background color from environment variables
    bg_color = os.getenv('BG_COLOR', '#FFFFFF')  # Default to white if not set

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

    return render_template("history.html", history=history, bg_color=bg_color)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

