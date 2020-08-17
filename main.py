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


@bot.message_handler(commands=['today'])
def today_info(message):
    status = postgresqllib.query(config, message.chat.id, Command.GET_CITY)
    if status is None:
        bot.send_message(message.chat.id, "Не установлен город. Какой город тебя интересует?")
    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")
    else:
        city, t, r, d = weatherlib.get_rain_info(status, config.appid)
        bot.send_message(message.chat.id, f"Погода в городе {city}.")
        if t is None and r is None and d is None:
            bot.send_message(message.chat.id, "Сегодня отличная погода.")
        if t is not None:
            bot.send_message(message.chat.id, f"Гроза в {t.strftime('%H:%M')}.")
        if r is not None:
            bot.send_message(message.chat.id, f"Дождь в {r.strftime('%H:%M')}.")
        if d is not None:
            bot.send_message(message.chat.id, f"Мелкий дождь в {d.strftime('%H:%M')}.")


@bot.message_handler(commands=['tomorrow'])
def tomorrow_info(message):
    pass  # todo


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
        try:
            city, _, _, _ = weatherlib.get_rain_info(message.text, config.appid)
            postgresqllib.query(config, message.chat.id, Command.SET_CITY, city)
            bot.send_message(message.chat.id, f"Информация обновлена. Текущий город - {city}.")
        except weatherlib.GetInfoError as e:
            if e.code == 404:
                bot.send_message(message.chat.id, "Кажется, такого города не существует. Повторите попытку.")
                return

    elif not status:
        bot.send_message(message.chat.id, "Ты не запустил бота. Воспользуйся командой /start.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
