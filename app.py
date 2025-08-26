from flask import Flask, render_template, request, session
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "203e28854cee3f930d9250998b472a6a"

API_KEY = "e741391ec872d58329d3d6c36a2c141f"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetchWeather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)
    
def parseWeather(data):
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "icon": data["weather"][0]["icon"]
    }
    
def save_to_recent_searches(city):
    # Initialize recent searches in session if it doesn't exist
    if 'recent_searches' not in session:
        session['recent_searches'] = []
    
    # Create a new search entry with timestamp
    new_search = {
        'city': city,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Add to the beginning of the list
    session['recent_searches'].insert(0, new_search)
    
    # Keep only the 5 most recent searches
    session['recent_searches'] = session['recent_searches'][:5]
    
    # Mark session as modified
    session.modified = True
        
@app.route('/', methods=["GET", "POST"])
def home():
    weather = None
    error = None
    
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            data, apiError = fetchWeather(city)
            if data:
                weather = parseWeather(data)
                save_to_recent_searches(city)
            else:
                error = apiError or "City not found or API error occurred"
    
    return render_template("index.html", weather=weather, error=error, 
                          recent_searches=session.get('recent_searches', []))

if __name__ == "__main__":
    app.run(debug=True)