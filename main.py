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
        msg += 'Похоже, ты уже запустил бота.'
        user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
        if user_city_id is not None:
            keyboard = get_main_menu()
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['rain'])
def rain_info(message):
    user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if user_city_id is None:
        msg += "Не установлен город. Какой город тебя интересует?"
    elif not user_city_id:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        user_city_name = weatherlib.get_city_name(user_city_id, config.appid)
        thunderstorm_time, rain_time, drizzle_time = weatherlib.get_rain_info(user_city_id, config.appid)
        msg += f"Город {user_city_name}:"
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
    user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
    user_city_name = weatherlib.get_city_name(user_city_id, config.appid)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    if user_city_id is None:
        msg += "Не установлен город. Какой город тебя интересует?"
    elif not user_city_id:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        weather = weatherlib.get_current_weather(user_city_id, config.appid)
        msg += f"Город {user_city_name}:\n"
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
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['city'])
def get_current_city(message):
    user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
    user_city_name = weatherlib.get_city_name(user_city_id, config.appid)
    msg = ""
    keyboard = types.ReplyKeyboardRemove()
    send_loc = False
    if user_city_id is None:
        msg += "Не установлен город. Какой город вас интересует?"
    elif not user_city_id:
        msg += "Ты не запустил бота. Воспользуйся командой /start."
    else:
        msg += f"Текущий город - {user_city_name}."
        keyboard = get_main_menu()
        send_loc = True
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    if send_loc:
        lat, lon = weatherlib.get_coordinates(user_city_id, config.appid)
        if lat is not None and lon is not None:
            bot.send_location(message.chat.id, lat, lon)
            bot.send_message(message.chat.id,
                             "Если город неверный, попробуйте сменить город и вместо названия отправить геопозицию.")


@bot.message_handler(commands=['admin_count'])
def admin_info(message):
    if message.chat.id != config.admin_id:
        process_message(message)
    else:
        count = database.query(config, message.chat.id, Command.GET_COUNT)
        bot.send_message(message.chat.id, f"Пользователей бота - {count}.", reply_markup=get_main_menu())


@bot.message_handler(content_types=['text'])
def process_message(message):
    user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
    if user_city_id is None:
        new_city_id, new_city_name = weatherlib.check_city(message.text, config.appid)
        if new_city_id is None:
            bot.send_message(message.chat.id, "Кажется, такого города не существует. Повторите попытку.")
        else:
            database.query(config, message.chat.id, Command.SET_CITY_ID, new_city_id)
            bot.send_message(message.chat.id, f"Информация обновлена. Текущий город - {new_city_name}.",
                             reply_markup=get_main_menu())
            lat, lon = weatherlib.get_coordinates(new_city_id, config.appid)
            if lat is not None and lon is not None:
                bot.send_location(message.chat.id, lat, lon)
                bot.send_message(message.chat.id,
                                 "Если город неверный, попробуйте сменить город и немного сместить геопозицию.")
    elif not user_city_id:
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


@bot.message_handler(content_types=['location'])
def process_location(message):
    user_city_id = database.query(config, message.chat.id, Command.GET_CITY_ID)
    if user_city_id is None:
        lat = message.location.latitude
        lon = message.location.longitude
        new_city_id, new_city_name = weatherlib.check_city_by_coordinates(lat, lon, config.appid)
        if new_city_id is None:
            bot.send_message(message.chat.id, "Извините, населенный пункт не определен. Повторите попытку.")
        else:
            database.query(config, message.chat.id, Command.SET_CITY_ID, new_city_id)
            bot.send_message(message.chat.id, f"Информация обновлена. Текущий город - {new_city_name}.",
                             reply_markup=get_main_menu())
            lat, lon = weatherlib.get_coordinates(new_city_id, config.appid)
            if lat is not None and lon is not None:
                bot.send_location(message.chat.id, lat, lon)
                bot.send_message(message.chat.id,
                                 "Если город неверный, попробуйте сменить город и немного сместить геопозицию.")
    elif not user_city_id:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        bot.send_message(message.chat.id, "Город уже установлен. Изменить его можно в меню.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
