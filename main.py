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
        msg = f"Город {status}:"
        if thunderstorm_time is None and rain_time is None and drizzle_time is None:
            msg += "\nДождя не ожидается."
        if thunderstorm_time is not None:
            msg += f"\nГроза в {thunderstorm_time.strftime('%H:%M')}."
        if rain_time is not None:
            msg += f"\nДождь в {rain_time.strftime('%H:%M')}."
        if drizzle_time is not None:
            msg += f"\nМелкий дождь в {drizzle_time.strftime('%H:%M')}."

        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['now'])
def current_weather(message):
    city = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if city is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город тебя интересует?")
    elif not city:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        weather = weatherlib.get_current_weather(city, config.appid)
        msg = f"Город {city}:\n"
        msg += f"{weather.description}.\n"
        msg += f"Температура: {weather.temperature}°C.\n"
        msg += f"Ощущается как {weather.feels_like}°C.\n"
        msg += f"Давление: {weather.pressure} мм рт.ст.\n"
        msg += f"Влажность: {weather.humidity}%.\n"
        msg += f"Ветер {weather.wind} м/с."

        bot.send_message(message.chat.id, msg)


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
    city = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if city is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город вас интересует?")
    elif not city:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        bot.send_message(message.chat.id, f"Текущий город - {city}.")


@bot.message_handler(commands=['admin_count'])
def admin_info(message):
    if message.chat.id != config.admin_id:
        process_message(message)
    else:
        count = postgresqllib.query(config, message.chat.id, Command.GET_COUNT)
        bot.send_message(message.chat.id, f"Пользователей бота - {count}.")


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
