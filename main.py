import telebot
import weatherlib
import config
import postgresqllib
from postgresqllib import Command

config = config.Config("config.json")

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_bot(message):
    status = postgresqllib.query(config, message.chat.id, Command.CREATE_USER)
    if status:
        bot.send_message(message.chat.id,
                         'Привет, я помогу тебе узнать прогноз погоды.')
        bot.send_message(message.chat.id,
                         'В каком городе ты находишься?\n(В дальнейшем город можно будет изменить командой /change)')
    else:
        bot.send_message(message.chat.id,
                         'Похоже, ты уже запустил бота. Можешь остановить его командой \n/stop или изменить город '
                         'командой \n/change.')


@bot.message_handler(commands=['rain'])
def rain_info(message):
    status = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if status is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город тебя интересует?")
    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        city = status
        thunderstorm_time, rain_time, drizzle_time = weatherlib.get_rain_info(city, config.appid)
        bot.send_message(message.chat.id, f"Погода в городе {status}:")
        if thunderstorm_time is None and rain_time is None and drizzle_time is None:
            bot.send_message(message.chat.id, "Сегодня отличная погода.")
        if thunderstorm_time is not None:
            bot.send_message(message.chat.id, f"Гроза в {thunderstorm_time.strftime('%H:%M')}.")
        if rain_time is not None:
            bot.send_message(message.chat.id, f"Дождь в {rain_time.strftime('%H:%M')}.")
        if drizzle_time is not None:
            bot.send_message(message.chat.id, f"Мелкий дождь в {drizzle_time.strftime('%H:%M')}.")


@bot.message_handler(commands=['now'])
def current_weather(message):
    status = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if status is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город тебя интересует?")
    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        city = status
        weather = weatherlib.get_current_weather(city, config.appid)
        bot.send_message(message.chat.id, f"Погода в городе {status}:")
        bot.send_message(message.chat.id, f"{weather.description}.")
        bot.send_message(message.chat.id, f"Температура: {weather.temperature}°C.")
        bot.send_message(message.chat.id, f"Ощущается как {weather.feels_like}°C.")
        bot.send_message(message.chat.id, f"Давление: {weather.pressure} мм рт.ст.")
        bot.send_message(message.chat.id, f"Влажность: {weather.humidity}%.")
        bot.send_message(message.chat.id, f"Ветер {weather.wind} м/с.")


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    status = postgresqllib.query(config, message.chat.id, Command.DELETE_USER)
    if not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        bot.send_message(message.chat.id, "Пока! Буду рад видеть тебя еще!")


@bot.message_handler(commands=['change'])
def change_city(message):
    status = postgresqllib.query(config, message.chat.id, Command.RESET_USER)
    if not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        bot.send_message(message.chat.id,
                         'В каком городе ты находишься?\n(В дальнейшем город можно будет изменить командой /change)')


@bot.message_handler(commands=['city'])
def get_current_city(message):
    status = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if status is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город вас интересует?")
    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        city = status
        bot.send_message(message.chat.id, f"Текущий город - {city}.")


@bot.message_handler(content_types=['text'])
def process_message(message):
    status = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if status is None:
        city = weatherlib.check_city(message.text, config.appid)
        if city is None:
            bot.send_message(message.chat.id, "Кажется, такого города не существует. Повторите попытку.")
        else:
            postgresqllib.query(config, message.chat.id, Command.SET_CITY, city)
            bot.send_message(message.chat.id, f"Информация обновлена. Текущий город - {city}.")
    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
