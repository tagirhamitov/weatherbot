import requests
from datetime import datetime, timezone, timedelta


class WeatherInfo:
    def __init__(self, data):
        self.description = data['weather'][0]['description'].capitalize()
        self.temperature = round(data['main']['temp'])
        self.feels_like = round(data['main']['feels_like'])
        self.pressure = round(data['main']['pressure'] / 1.333)
        self.humidity = round(data['main']['humidity'])
        self.wind = round(data['wind']['speed'])


def send_request(city, appid, query_type):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/{query_type}",
                     params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
    data = r.json()
    return data


def check_city(city, appid):
    data = send_request(city, appid, "weather")
    if data["cod"] != 200:
        return None
    else:
        return data["name"]


def get_rain_info(city, appid):
    data = send_request(city, appid, "forecast")

    tz = timezone(timedelta(seconds=data['city']['timezone']))
    today = datetime.now(tz)

    thunderstorm_time = None
    drizzle_time = None
    rain_time = None

    for item in data['list']:
        dt = datetime.fromtimestamp(item['dt'], tz)
        if dt.day > today.day:
            break
        for weather in item['weather']:
            code = weather['id'] // 100
            if code == 2 and thunderstorm_time is None:
                thunderstorm_time = dt
            elif code == 3 and drizzle_time is None:
                drizzle_time = dt
            elif code == 5 and rain_time is None:
                rain_time = dt

    return thunderstorm_time, rain_time, drizzle_time


def get_current_weather(city, appid):
    data = send_request(city, appid, "weather")
    return WeatherInfo(data)
