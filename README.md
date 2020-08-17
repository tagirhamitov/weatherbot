The weather bot for telegram.<br>
<br>
(Only Russian language is supported)<br>
<br>
Current working commands:<br>
```/start``` - start the bot<br>
```/stop``` - stop the bot<br>
```/change``` - change current city<br>
```/city``` - view current city<br>
```/today``` - view today's weather<br>
<br>
To run this bot you need:<br>
1) Register bot in <a href="https://t.me/botfather">@BotFather</a> and get token.<br>
2) Register in <a href="https://openweathermap.org">openweathermap.org</a> and get api key.<br>
3) Get login, password, database and host for PostgreSQL.<br>
4) Clone this repository:<br>
```git clone https://github.com/tagirhamitov/weatherbot.git```<br>
```cd weatherbot```<br>
5) Create file ```config.json```. Example:<br>
```
{
    "token": "YOUR_TELEGRAM_TOKEN_HERE",
    "appid": "YOUR_OPENWEATHERMAP_API_KEY_HERE",
    "login": "YOUR_POSTGRESQL_LOGIN_HERE",
    "password": "YOUR_POSTGRESQL_PASSWORD_HERE",
    "db_name": "YOUR_POSTGRESQL_DATABASE_NAME_HERE",
    "host": "YOUR_POSTGRESQL_HOST_HERE"
}
```
6) Run ```main.py```<br>
7) If you want to deploy the bot to heroku, set environment variables token, appid, login, password, db_name and host with their values in heroku settings. And define an empty environ variable HEROKU.