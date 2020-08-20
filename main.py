import telebot
import weatherlib
import config
import postgresqllib as database
from postgresqllib import Command
from telebot import types

config = config.Config("config.json")

bot = telebot.TeleBot(config.token)


def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Прогноз погоды")
    keyboard.row("Сменить город", "Текущий город")
    keyboard.row("Остановить бота")
    return keyboard


def get_weather_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Погода сейчас")
    keyboard.row("Будет ли дождь")
    keyboard.row("Назад")
    return keyboard


@bot.message_handler(commands=['start'])
def start_bot(message):
    status = database.query(config, message.chat.id, Command.CREATE_USER)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if status:
        msg += "Привет, я помогу тебе узнать прогноз погоды.\n"
        msg += "В каком городе ты находишься?"
    else:
        msg += 'Похоже, ты уже запустил бота. Можешь остановить его командой \n/stop или изменить город командой ' \
               '\n/change. '
        user_city = database.query(config, message.chat.id, Command.GET_CITY)
        if user_city is not None:
            keyboard = get_main_menu()
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['rain'])
def rain_info(message):
    user_city = database.query(config, message.chat.id, Command.GET_CITY)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if user_city is None:
        msg += "Не установлен город. Какой город тебя интересует?"
    elif not user_city:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        thunderstorm_time, rain_time, drizzle_time = weatherlib.get_rain_info(user_city, config.appid)
        msg += f"Город {user_city}:"
        if thunderstorm_time is None and rain_time is None and drizzle_time is None:
            msg += "\nДождя не ожидается."
        if thunderstorm_time is not None:
            msg += f"\nГроза в {thunderstorm_time.strftime('%H:%M')}."
        if rain_time is not None:
            msg += f"\nДождь в {rain_time.strftime('%H:%M')}."
        if drizzle_time is not None:
            msg += f"\nМелкий дождь в {drizzle_time.strftime('%H:%M')}."
        keyboard = get_main_menu()
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['now'])
def current_weather(message):
    user_city = database.query(config, message.chat.id, Command.GET_CITY)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if user_city is None:
        msg += "Не установлен город. Какой город тебя интересует?"
    elif not user_city:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        weather = weatherlib.get_current_weather(user_city, config.appid)
        msg += f"Город {user_city}:\n"
        msg += f"{weather.description}.\n"
        msg += f"Температура: {weather.temperature}°C.\n"
        msg += f"Ощущается как {weather.feels_like}°C.\n"
        msg += f"Давление: {weather.pressure} мм рт.ст.\n"
        msg += f"Влажность: {weather.humidity}%.\n"
        msg += f"Ветер {weather.wind} м/с."
        keyboard = get_main_menu()
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    status = database.query(config, message.chat.id, Command.DELETE_USER)
    msg = ""
    keyboard = types.ReplyKeyboardRemove(0)
    if not status:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        msg += "Пока! Буду рад видеть тебя еще!\n"
        msg += "Запустить бота - /start"
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['change'])
def change_city(message):
    status = database.query(config, message.chat.id, Command.RESET_USER)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if not status:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        msg += "В каком городе ты находишься?\n"
        msg += "(В дальнейшем город можно будет изменить командой /change)"
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['city'])
def get_current_city(message):
    user_city = database.query(config, message.chat.id, Command.GET_CITY)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if user_city is None:
        msg += "Не установлен город. Какой город вас интересует?"
    elif not user_city:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        msg += f"Текущий город - {user_city}."
        keyboard = get_main_menu()
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['admin_count'])
def admin_info(message):
    if message.chat.id != config.admin_id:
        process_message(message)
    else:
        count = database.query(config, message.chat.id, Command.GET_COUNT)
        bot.send_message(message.chat.id, f"Пользователей бота - {count}.", reply_markup=get_main_menu())


@bot.message_handler(content_types=['text'])
def process_message(message):
    user_city = database.query(config, message.chat.id, Command.GET_CITY)
    if user_city is None:
        new_city = weatherlib.check_city(message.text, config.appid)
        if new_city is None:
            bot.send_message(message.chat.id, "Кажется, такого города не существует. Повторите попытку.")
        else:
            database.query(config, message.chat.id, Command.SET_CITY, new_city)
            bot.send_message(message.chat.id, f"Информация обновлена. Текущий город - {new_city}.",
                             reply_markup=get_main_menu())
    elif not user_city:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        if message.text == "Прогноз погоды":
            bot.send_message(message.chat.id, "Выберите тип прогноза.", reply_markup=get_weather_menu())
        elif message.text == "Сменить город":
            change_city(message)
        elif message.text == "Текущий город":
            get_current_city(message)
        elif message.text == "Остановить бота":
            stop_bot(message)
        elif message.text == "Погода сейчас":
            current_weather(message)
        elif message.text == "Будет ли дождь":
            rain_info(message)
        elif message.text == "Назад":
            bot.send_message(message.chat.id, "Выберите пункт меню.", reply_markup=get_main_menu())
        else:
            bot.send_message(message.chat.id, "Неизвестная команда.", reply_markup=get_main_menu())


if __name__ == "__main__":
    bot.polling(none_stop=True)
