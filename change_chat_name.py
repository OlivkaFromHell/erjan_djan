# -*- coding: utf8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import datetime as dt
import time
from config import token
from info import list_of_dates, dates_of_birth
from pprint import pprint

vk_session = vk_api.VkApi(token=token)  # Передаем токен сообщества
vk = vk_session.get_api()
groupId = 202528897  # id беседы Джа 20


def change_chat_name(title, chat_id):  # функция меняет название беседы
    return vk_session.method('messages.editChat',
                             {'chat_id': chat_id, 'title': title})


default_chat_name = 'Джа’21 🚌'
chat_id = 2

if __name__ == '__main__':
    now = dt.datetime.now() # текущее время и дата
    today = f"{now.day} {now.month}"  # сегодня
    current_title = vk_session.method("messages.getConversationsById",
                                      {'peer_ids': 2000000000 + chat_id})['items'][0]['chat_settings']['title']
    if today in dates_of_birth:
        change_chat_name(dates_of_birth[today], chat_id)
    elif current_title != default_chat_name:
        change_chat_name(default_chat_name, chat_id)
