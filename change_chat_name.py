# -*- coding: utf8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import datetime as dt
import time
from config import token
from info import list_of_dates, dates_of_birth

vk_session = vk_api.VkApi(token=token)  # Передаем токен сообщества
vk = vk_session.get_api()
groupId = 202528897  # id беседы Джа 20


def change_chat_name(title):  # функция меняет название беседы
    return vk_session.method('messages.editChat',
                            {'chat_id': 2, 'title': title})

def send_msg(id, text):
    return vk_session.method("messages.send", {'chat_id': id, 'message': text, "random_id": 0})

default_chat_name = 'Джа’21 🚌'
while True:
    try:
        while True:
            now = dt.datetime.now()  # текущее время и дата
            today = f"{now.day} {now.month}"  # сегодня
            next_today = f"{now.day} {now.month}"  # дубл сегодняшнюю дату для поиска
            next_now = dt.datetime.now()  # дублируем дату по datetime
            if today in dates_of_birth:  # если сегодня др
                change_chat_name(dates_of_birth[today])  # меняем название беседы
                number_date = list_of_dates.index(today) + 1
                time.sleep((24 - now.hour)*3600 + 8*3600)  # усыпляем на сутки, чтобы на след день поменять
                change_chat_name(default_chat_name)
            else:
                while next_today not in dates_of_birth:  # пока не найдем след др
                    next_now = next_now + dt.timedelta(days=1)  # идем на след день
                    next_today = f"{next_now.day} {next_now.month}"
                number_date = list_of_dates.index(next_today)

            next_birth_day, next_birth_month = list_of_dates[number_date].split()
            next_birth = dt.datetime(now.year, 
                int(next_birth_month), int(next_birth_day), 8, 0)  # След др в 8:00
            between_birth = next_birth - now  # разница между др
            time.sleep(between_birth.days*86400 + between_birth.seconds)
    except Exception:
        send_msg(1, 'Что-то не так с day_birth')