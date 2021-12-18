import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from time import sleep

from config import token
from weather import for_day_weather


def send_msg(id, text):
    sleep(0.5)
    return vk_session.method("messages.send",
                             {'chat_id': id,
                              'message': text,
                              "random_id": 0})


def send_weather():
    send_msg(2, for_day_weather())


vk_session = vk_api.VkApi(token=token)  # Передаем токен сообщества
vk = vk_session.get_api()
groupId = 202528897
longpoll = VkBotLongPoll(vk_session, groupId)

if __name__ == "__main__":
    send_weather()
