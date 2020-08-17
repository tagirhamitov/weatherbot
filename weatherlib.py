import requests
from datetime import datetime, timezone, timedelta


class GetInfoError(Exception):
    def __init__(self, code):
        self.code = code


def get_rain_info(city_name, appid):
    if not isinstance(city_name, str):
        raise ValueError("city_name must be string")

    if not isinstance(appid, str):
        raise ValueError("appid must be string")

    r = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                     params={'q': city_name, 'units': 'metric', 'lang': 'ru', 'APPID': appid})

    data = r.json()
    if data["cod"] == "404":
        raise GetInfoError(404)
    elif data["cod"] == "401":
        raise GetInfoError(401)

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

    local_name = data['city']['name']

    return local_name, thunderstorm_time, rain_time, drizzle_time
