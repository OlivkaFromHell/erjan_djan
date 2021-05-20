import re
import os
import requests
import datetime as dt 
from time import sleep
from random import random, randrange

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from weather import current_weather
from gif_maker import create_gif, shakalize

# information files
from config import token
from info import number_base

vk_session = vk_api.VkApi(token=token)  # Передаем токен сообщества
vk = vk_session.get_api()
groupId = 202528897
longpoll = VkBotLongPoll(vk_session, groupId)

def send_msg(id, text):
    sleep(0.5)
    return vk_session.method("messages.send",
            {'chat_id': id,
             'message': text,
             "random_id": 0})

def send_photo(id, attachment): # функция отправки сообщения в чат
    sleep(0.3)
    return vk_session.method("messages.send",
            {'chat_id': id,
             'attachment': attachment,
             "random_id": 0})

def season_left_days(id):
    """отправляет кол-во дней до сезона"""
    now = dt.datetime.now()
    send_msg(id, f"До сезона осталось {(season - now).days} дней")

def zhd_left_days(id):
    """отправляет фото ержана с пивом и кол-во дней до зхд"""
    # pictures_zhd = ['photo-202528897_457239152', 'photo-202528897_457239154', 
    #             'photo-202528897_457239153', 'photo-202528897_457239157', 
    #             'photo-202528897_457239155', 'photo-202528897_457239156']

    now = dt.datetime.now()
    send_msg(id, f"До заходского осталось {(zhd - now).days} дней")
    send_photo(id, 'photo-202528897_457239087')

def how_much_erjan_working(id):
    """пишет количество отработанных ержанном часов без перезапуска"""
    now = dt.datetime.now()
    time_left = now - start_work 
    hour = round(time_left.seconds/3600)
    if time_left.days == 0:
        send_msg(id, f'{hour} часов, начальник')
    elif hour == 0:
        send_msg(id, f'{time_left.days} дней, начальник')
    else:
        send_msg(id, f'{time_left.days} дней и {hour} часов, начальник')

def send_photo_from_folder(id, path):
    """Загрузка фотографий на vk.UploadServer с сервера и дальнейшая 
    отправка в личные сообщения или чат"""
    server = vk.photos.getMessagesUploadServer()

    photo = requests.post(server['upload_url'], files={'photo': open(path, 'rb')}).json()
    save_photo = vk.photos.saveMessagesPhoto(photo=photo['photo'], server=photo['server'], hash=photo['hash'])[0]
    upload_ph = "photo{}_{}".format(save_photo['owner_id'], save_photo['id'])
    vk_session.method('messages.send', {'chat_id': id, 'message': ' ', 'attachment': upload_ph, 'random_id': 0})

def send_doc(d, path):
    """отправляем любые доки"""
    # vk - <class 'vk_api.vk_api.VkApiMethod'>
    doc = vk_api.upload.VkUpload(vk).document_message(open(path, 'rb'), peer_id=2_000_000_000+id)
    upload_doc = 'doc{}_{}'.format(doc['doc']['owner_id'], doc['doc']['id'])
    vk_session.method('messages.send', {'chat_id': id, 'message': ' ', 'attachment': upload_doc, 'random_id': 0})

def download_photo(event):
    amount_of_photos = len(event.object.message['attachments'])
    for i in range(amount_of_photos):
        m = []
        resolutions = event.object.message['attachments'][i]['photo']['sizes']
        for link in resolutions:
            m.append(link['height'])

        max_resolution = m.index(max(m))
        url = event.object.message['attachments'][i]['photo']['sizes'][max_resolution]['url']
        
        r = requests.get(url)

        with open('photo/{}.jpg'.format(i), 'wb') as ph:
            ph.write(r.content)

    return amount_of_photos

def send_gif(id, event):
    amount_of_photos = download_photo(event)
    photos = []
    for i in range(amount_of_photos):
        photos.append('photo/{}.jpg'.format(i))
    print(amount_of_photos)
    create_gif(photos)
    send_doc(id, 'photo/erj.gif')

def send_shakal(id, event):
    resolutions = event.object.message['attachments'][0]['photo']['sizes']
    m = []
    for link in resolutions:
        m.append(link['height'])

    max_resolution = m.index(max(m))
    url = event.object.message['attachments'][0]['photo']['sizes'][max_resolution]['url']

    r = requests.get(url)

    with open('photo/shakal/pic.jpg', 'wb') as ph:
        ph.write(r.content)

    shakalize('photo/shakal/pic.jpg')
    send_photo_from_folder(id, 'photo/shakal/shakal.jpg')

def send_ultrashakal(id, event):
    resolutions = event.object.message['attachments'][0]['photo']['sizes']
    m = []
    for link in resolutions:
        m.append(link['height'])

    max_resolution = m.index(max(m))
    url = event.object.message['attachments'][0]['photo']['sizes'][max_resolution]['url']

    r = requests.get(url)

    with open('photo/shakal/pic.jpg', 'wb') as ph:
        ph.write(r.content)

    shakalize('photo/shakal/pic.jpg', quality= 1)
    send_photo_from_folder(id, 'photo/shakal/shakal.jpg')


season = dt.datetime(2021, 7, 1)
zhd = dt.datetime(2021, 9, 18)

# патерны для поиск в сообщение шаблонов
# вот это хорошо было бы обернуть в словарь и вынести в другой файл
pattern_phone = r'(?i).*(ержан|джа)?.*(какой|киньт?е?)?.*номер.у?.?\[\w\w(\d+)|.+' # шаблон поиска запроса
pattern_days_left_to_season = r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*до.+сезона.*\??'
pattern_days_left_to_zhd = r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*(до)?.*(зхд|заходское|заходского).*\??'
pattern_erjan = r'(?i).*ержан.*\?$'
pattern_understand = r'(?i).*не понял\.?$'
pattern_hui = r'(?i).*иди нахуй$' 
pattern_how_many = r'(?i).*сколько.*'
pattern_go = r'(?i).*ержан.* (го|погнали|пойдем|пошли).*'
pattern_rso = r'(?i).*труд.*'
pattern_weather = r'(?i).*ержан.*погода.*'



start_work = dt.datetime.now() # ержан начал работать
while True:
    try:
        for event in longpoll.listen(): 
            if event.type == VkBotEventType.MESSAGE_NEW: 
                try:
                    if event.from_chat:
                        number = randrange(1, 1000)  
                        id = event.chat_id

                        msg = str(event.object.message['text']) 
                        id_user = re.match(pattern_phone, msg).group(3) # записываем id

                        days_left_to_season = re.match(pattern_days_left_to_season, msg) # сколько дней до сезона?
                        days_left_to_zhd = re.match(pattern_days_left_to_zhd, msg) # сколько дней до зхд
                        erj_que = re.match(pattern_erjan, msg) # ищет вопрос ержану
                        understand = re.match(pattern_understand, msg) # ищет сочетание не понял
                        how_many = re.match(pattern_how_many, msg) # ищет вопрос сколько
                        nahui = re.match(pattern_hui, msg) # ержана послали нахуй?
                        pognali = re.match(pattern_go, msg) # ержана зовут бухать
                        rso = re.match(pattern_rso, msg) # любим рсо
                        weather_now = re.match(pattern_weather, msg) # погода

                        if id_user and (int(id_user.group(3)) in number_base):
                            send_msg(id, f"Номер {number_base[int(id_user.group(3))][1]}: {number_base[int(id_user.group(3))][0]}")

                        elif days_left_to_season or msg == '!сезон':
                            season_left_days(id)

                        elif days_left_to_zhd or msg == '!зхд':
                            zhd_left_days(id)

                        elif (msg == 'Да' or msg == 'да' or msg == 'ДА') and number < 150:
                            send_msg(id, 'Манда')
                        elif (msg == 'Нет' or msg == 'нет' or msg == 'НЕТ') and number < 150:
                            send_msg(id, 'Пидора ответ')
                        elif msg == 'Ержан,работаешь?':  # проверка бота работоспособность
                            send_photo(id, 'photo-202528897_457239027')

                        elif msg == 'Ержан, давно работаешь?' or msg == '!работа':
                            how_much_erjan_working(id)

                        elif msg == 'Ержан, сделай гифку':
                            send_gif(id, event)

                        elif msg == 'Ержан, шакализируй' or msg == 'Ержан, шакал':
                            send_shakal(id, event)

                        elif msg == 'Ержан, ультрашакал':
                            send_ultrashakal(id, event)

                        # elif msg == 'Ержан, пиши диплом':
                        #     send_photo(id, 'photo-202528897_457239141')

                        elif weather_now or msg == '!погода':
                            send_msg(id, current_weather())

                        elif pognali: # ержан погнали/го/пойдем
                            if number < 300:
                                send_msg(id, 'выезжаю')
                            elif number <600:
                                send_msg(id, 'без деда никуда не пойду')
                            elif number <900:
                                send_msg(id, 'погнали')
                            elif number > 900:
                                send_msg(id, 'с дедом хоть на край света')

                        elif how_many:  # вопросы с ключом сколько
                            if number > 800:
                                send_msg(id, 'дохуя')
                            else:
                                send_msg(id, round(number/10))

                        elif rso: # триггер на слова с "труд"
                            send_msg(id, 'Я люблю РСО 🏳️‍🌈 🏳️‍🌈 🏳️‍🌈')  

                        elif erj_que: # вопросы к ержану
                            if number < 251:
                                send_msg(id, 'да')
                            if 250 < number < 501:
                                send_msg(id, 'нет')
                            if 500 < number < 751:
                                send_msg(id, 'мне поебать')
                            if 750 < number < 801:
                                send_msg(id, 'суета')
                            if 800 < number < 821:
                                send_msg(id, 'один раз не пидорас')
                            if 820 < number < 851:
                                send_msg(id, 'узнаешь')
                            
                            if 850 < number < 876:
                                send_msg(id, 'я больше не работаю')
                            if 875 < number < 881:
                                send_msg(id, 'Я, блять, в своём познании настолько преисполнился, \
                                    что я как будто бы уже 100 триллионов миллиардов лет, блять,\
                                    проживаю на триллионах и триллионах таких же планет, понимаешь?\
                                    Как эта Земля. Мне уже этот мир абсолютно понятен, и я здесь ищу\
                                    только одного: покоя, умиротворения и вот этой гармонии от слияния \
                                    с бесконечно вечным.')
                            if 880 < number < 886:
                                send_msg(id, 'Как вам сказать… \
                                    Я прожила довольно долгую жизнь… \
                                    Ибрагим вам что-нибудь говорит?\
                                    Прекрасное имя. Аллах акбар. \
                                    Я прошла афганскую войну. И я желаю всем мужчинам пройти ее.\
                                    Мужчина определяется делом, а не словом.\
                                    И если я ношу кандибобер на голове, это не значит,\
                                    что я женщина или балерина')
                            if 885 < number < 926:
                                send_msg(id, 'отвечаю')
                            if 925 < number < 951:
                                send_msg(id, 'Ахахах, насмешил. Гуляй')
                            if 950 < number < 991:
                                send_msg(id, 'по-любому, езжи')
                            if 990 < number < 1001:
                                send_msg(id, 'встану - ты ляжешь')
                            
                        elif (msg == 'Веселое' or msg == 'Весёлое') and number < 500:
                            send_msg(id, 'Нет блин грустное')    

                        elif understand and number < 300: # не понял
                            send_msg(id, 'поймешь')

                        elif nahui and number > 700: # ержана послали нахуй
                            send_msg(id, 'Сам нахуй иди')

                        elif msg == 'один раз': # no comments
                            send_msg(id, 'не пидорас')

                        # удаляем все файлы в каталоге photo 
                        # filelist = [ f for f in os.listdir('photo')]
                        # for f in filelist:
                        #     os.remove(os.path.join('photo', f))

                except Exception as e:
                    print(e)
                   
    except Exception:
        send_msg(1, 'Сервер перезагрузился')
