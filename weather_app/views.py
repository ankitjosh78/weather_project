from django.shortcuts import render
import requests
from datetime import datetime, timedelta
from weather_project.settings import API_KEY


BASE_URL = "https://api.openweathermap.org/data/2.5/"


def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def get_forecast_weather(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def format_forecast_data(forecast_data):
    forecast_dict = {}
    for item in forecast_data["list"]:
        date = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
        if date not in forecast_dict:
            forecast_dict[date] = {"temps": [], "descriptions": str()}
        forecast_dict[date]["temps"].append(item["main"]["temp"])
        forecast_dict[date]["descriptions"] = item["weather"][0][
            "description"
        ].capitalize()
        forecast_dict[date]["icon"] = item["weather"][0]["icon"]

    formatted_data = []
    for date, data in forecast_dict.items():
        formatted_item = {
            "date": date.strftime("%A, %d %B"),
            "min_temp": min(data["temps"]),
            "max_temp": max(data["temps"]),
            "descriptions": "".join(data["descriptions"]),
            "icon": data["icon"],
        }
        formatted_data.append(formatted_item)

    return formatted_data[:5]  # Return only the next 5 days


def get_today_temperatures(forecast_data):
    today = datetime.today().date()
    today_temps = []
    for item in forecast_data["list"]:
        dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
        if dt.date() == today:
            item["hour"] = dt.strftime(
                "%H:00"
            )  # Extract only the hour and add it to the item
            today_temps.append(item)
    return today_temps


def index(request):
    city = None
    current_weather_data = None
    forecast_weather_data = None
    formatted_forecast_data = None
    today_temperatures = None

    if request.method == "GET" and "city" in request.GET:
        city = request.GET.get("city")
        current_weather_data = get_current_weather(city)
        forecast_weather_data = get_forecast_weather(city)
        if forecast_weather_data:
            formatted_forecast_data = format_forecast_data(forecast_weather_data)
            today_temperatures = get_today_temperatures(forecast_weather_data)

    return render(
        request,
        "weather_app/weather.html",
        {
            "current_weather_data": current_weather_data,
            "formatted_forecast_data": formatted_forecast_data,
            "today_temperatures": today_temperatures,
            "city": city,
        },
    )
