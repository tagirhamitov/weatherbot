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


def send_request_by_city_id(city_id, appid, query_type):
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/{query_type}",
        params={
            'id': city_id,
            'units': 'metric',
            'lang': 'ru',
            'appid': appid,
        }
    )
    data = response.json()
    return data


def send_request_by_city_name(city_name, appid, query_type):
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/{query_type}",
        params={
            'q': city_name,
            'units': 'metric',
            'lang': 'ru',
            'appid': appid,
        }
    )
    data = response.json()
    return data


def send_request_by_coordinates(lat, lon, appid, query_type):
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/{query_type}",
        params={
            'lat': lat,
            'lon': lon,
            'units': 'metric',
            'lang': 'ru',
            'appid': appid,
        }
    )
    data = response.json()
    return data


def check_city(city_name, appid):
    data = send_request_by_city_name(city_name, appid, "weather")
    if data["cod"] != 200:
        return None, None
    else:
        return data["id"], data["name"]


def get_city_name(city_id, appid):
    data = send_request_by_city_id(city_id, appid, "weather")
    if data["cod"] != 200:
        return None
    else:
        return data["name"]


def check_city_by_coordinates(lat, lon, appid):
    data = send_request_by_coordinates(lat, lon, appid, "weather")
    if data["cod"] != 200:
        return None, None
    else:
        return data["id"], data["name"]


def get_coordinates(city_id, appid):
    data = send_request_by_city_id(city_id, appid, "weather")
    if data["cod"] != 200:
        return None, None
    else:
        return data["coord"]["lat"], data["coord"]["lon"]


def get_rain_info(city_id, appid):
    data = send_request_by_city_id(city_id, appid, "forecast")

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


def get_current_weather(city_id, appid):
    data = send_request_by_city_id(city_id, appid, "weather")
    return WeatherInfo(data)
