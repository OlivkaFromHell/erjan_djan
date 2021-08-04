import random
import re
import requests
import datetime as dt
from time import sleep
from random import randrange, choice

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from weather import current_weather, time_of_sunrise, time_of_sunset
# from gif_maker import create_gif, shakalize

# information files
from config import token, groupId
from info import number_base, sber_card_number, sber_phone_number

vk_session = vk_api.VkApi(token=token)  # Передаем токен сообщества
vk = vk_session.get_api()
groupId = groupId
longpoll = VkBotLongPoll(vk_session, groupId)


def send_msg(id, text, attachment=''):
    sleep(0.5)
    return vk_session.method("messages.send",
                             {'chat_id': id,
                              'message': text,
                              'attachment': attachment,
                              'random_id': 0})


def send_photo(id, attachment):
    """отправляем фото в чат"""
    sleep(0.3)
    return vk_session.method("messages.send",
                             {'chat_id': id,
                              'attachment': attachment,
                              "random_id": 0})


def end_of_days_wrapper(func):
    def wrapper(id):
        now = dt.datetime.now()
        days_left = (zhd - now).days
        if days_left % 10 == 1:
            sentence_end = 'день'
        elif days_left % 10 in (2, 3, 4):
            sentence_end = 'дня'
        else:
            sentence_end = 'дней'
        return func(id, sentence_end=sentence_end)
    return wrapper


@end_of_days_wrapper
def season_left_days(id, sentence_end='дней'):
    """отправляет кол-во дней до сезона"""
    now = dt.datetime.now()
    days_left = (zhd - now).days
    send_msg(id, f"До конца сезона осталось {days_left} {sentence_end}", attachment='photo-202528897_457239185')


@end_of_days_wrapper
def zhd_left_days(id, sentence_end='дней'):
    """отправляет фото ержана с пивом и кол-во дней до зхд"""
    # pictures_zhd = ['photo-202528897_457239152', 'photo-202528897_457239154', 
    #             'photo-202528897_457239153', 'photo-202528897_457239157', 
    #             'photo-202528897_457239155', 'photo-202528897_457239156']

    now = dt.datetime.now()
    days_left = (zhd - now).days
    send_msg(id, f"До заходского осталось {days_left} {sentence_end}", attachment='photo-202528897_457239087')


@end_of_days_wrapper
def how_much_erjan_working(id, sentence_end='дней'):
    """пишет количество отработанных ержанном часов без перезапуска"""
    now = dt.datetime.now()
    time_left = now - start_work
    hour = round(time_left.seconds / 3600)
    if time_left.days == 0:
        send_msg(id, f'{hour} часов, начальник')
    elif hour == 0:
        send_msg(id, f'{time_left.days} {sentence_end}, начальник')
    else:
        send_msg(id, f'{time_left.days} {sentence_end} и {hour} часов, начальник')


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
    doc = vk_api.upload.VkUpload(vk).document_message(open(path, 'rb'), peer_id=2_000_000_000 + id)
    upload_doc = 'doc{}_{}'.format(doc['doc']['owner_id'], doc['doc']['id'])
    vk_session.method('messages.send', {'chat_id': id, 'message': ' ', 'attachment': upload_doc, 'random_id': 0})


def download_photo(event):
    """Скачивает все изображения из сообщения"""
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
    """отправляет гифку, хранящуюся внутри директориии photo"""
    amount_of_photos = download_photo(event)
    photos = []
    for i in range(amount_of_photos):
        photos.append('photo/{}.jpg'.format(i))
    print(amount_of_photos)
    create_gif(photos)
    send_doc(id, 'photo/erj.gif')


def send_shakal(id, event):
    """Отправляет просто сжатую картинку пользователю"""
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
    """Отправляет очень сжатую картинку пользователю"""
    resolutions = event.object.message['attachments'][0]['photo']['sizes']
    m = []
    for link in resolutions:
        m.append(link['height'])

    max_resolution = m.index(max(m))
    url = event.object.message['attachments'][0]['photo']['sizes'][max_resolution]['url']

    r = requests.get(url)

    with open('photo/shakal/pic.jpg', 'wb') as ph:
        ph.write(r.content)

    shakalize('photo/shakal/pic.jpg', quality=1)
    send_photo_from_folder(id, 'photo/shakal/shakal.jpg')


season = dt.datetime(2021, 8, 29)
zhd = dt.datetime(2021, 9, 18)

# патерны для поиск в сообщение шаблонов

patterns = {
    'pattern_phone': r'(?i).*(ержан|джа)?.*(какой|киньт?е?)?.*номер.у?.?\[\w\w(\d+)|.+',
    'pattern_days_left_to_season': r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*до.+сезона.*\??',
    'pattern_days_left_to_zhd': r'(?i).*(ержан|джа)?.*сколько.+(дней)?.*(до)?.*(зхд|заходское|заходского).*\??',
    'pattern_erjan': r'(?i).*ержан.*\?$',
    'pattern_understand': r'(?i).*не понял\.?$',
    'pattern_hui': r'(?i).*иди нахуй$',
    'pattern_how_many': r'(?i).*сколько.*',
    'pattern_go': r'(?i).*ержан.* (го|погнали|пойдем|пошли).*',
    'pattern_rso': r'(?i).*труд.*',
    'pattern_weather': r'(?i).*ержан.*погода.*',
    'pattern_veseloe': r'(?i).*(веселое|весёлое).*',
    'pattern_sber': r'(?i).*(карт).*(сбер).*',
    ################################################
    'pattern_5': r'(?i).*(карт).*(пятероч).*',
    'pattern_lenta': r'(?i).*(карт).*(ленты|лента).*',
    'pattern_perek': r'(?i).*(карт).*(перек|перекрест).*',
    'pattern_magnit': r'(?i).*(карт).*(магнит).*',
    'pattern_okey': r'(?i).*(карт).*(магнит).*',
    'pattern_prisma': r'(?i).*(карт).*(призм).*',
    'pattern_sportmaster': r'(?i).*(карт).*(спортмастер).*',
    'pattern_trial_sport': r'(?i).*(карт).*(триал спорт).*',
}

loyality_cards = {
    '5': ['photo-202528897_457239175'],
    'lenta': ['photo-202528897_457239178', 'photo-202528897_457239189', 'photo-202528897_457239190'],
    'perek': ['photo-202528897_457239181'],
    'magnit': ['photo-202528897_457239179'],
    'okey': ['photo-202528897_457239180', 'photo-202528897_457239188'],
    'prisma': ['photo-202528897_457239174'],
    'sportmaster': ['photo-202528897_457239176'],
    'trial_sport': ['photo-202528897_457239177'],
}

start_work = dt.datetime.now()  # ержан начал работать
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    if event.from_chat:
                        number = randrange(1, 1000)
                        id = event.chat_id
                        msg = str(event.object.message['text'])
                        id_user = re.match(patterns['pattern_phone'], msg).group(3)

                        if re.match(patterns['pattern_go'], msg):  # ержана зовут бухать
                            if number < 300:
                                send_msg(id, 'выезжаю')
                            elif number < 600:
                                send_msg(id, 'без деда никуда не пойду')
                            elif number < 900:
                                send_msg(id, 'погнали')
                            elif number > 900:
                                send_msg(id, 'с дедом хоть на край света')

                        elif (msg == '!погода') or re.match(patterns['pattern_weather'], msg):  # погода
                            send_msg(id, current_weather())

                        # сколько дней до зхд
                        elif (msg == '!зхд') or re.match(patterns['pattern_days_left_to_zhd'], msg):
                            zhd_left_days(id)

                        elif re.match(patterns['pattern_how_many'], msg):  # ищет вопрос сколько
                            if number > 800:
                                send_msg(id, 'дохуя')
                            else:
                                send_msg(id, round(number / 10))

                        elif msg == 'Ержан, работаешь?':  # проверка бота работоспособность
                            send_photo(id, 'photo-202528897_457239027')

                        elif msg == 'Ержан, который час?':
                            send_msg(id, 'время пива!')

                        elif msg == 'Ержан, давно работаешь?' or msg == '!работа':
                            how_much_erjan_working(id)

                        elif id_user and int(id_user) in number_base:  # записываем id
                            send_msg(id, f"Номер {number_base[int(id_user)][1]}: {number_base[int(id_user)][0]}")

                        elif msg == '!сбер' or re.match(patterns['pattern_sber'], msg):
                            ans = f'Да, жду бананы\n\n{sber_card_number}\n{sber_phone_number}'
                            send_msg(id, ans)

                        # loyalty cards block
                        elif msg == '!пятерочка' or re.match(patterns['pattern_5'], msg):
                            attachment = random.choice(loyality_cards['5'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!перекресток' or msg == '!перек' or re.match(patterns['pattern_perek'], msg):
                            attachment = random.choice(loyality_cards['perek'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!лента' or re.match(patterns['pattern_lenta'], msg):
                            attachment = random.choice(loyality_cards['lenta'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!магнит' or re.match(patterns['pattern_magnit'], msg):
                            attachment = random.choice(loyality_cards['magnit'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!призма' or re.match(patterns['pattern_prisma'], msg):
                            attachment = random.choice(loyality_cards['prisma'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!окей' or re.match(patterns['pattern_okey'], msg):
                            attachment = random.choice(loyality_cards['okey'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!триал спорт' or re.match(patterns['pattern_trial_sport'], msg):
                            attachment = random.choice(loyality_cards['trial_sport'])
                            send_msg(id, text='держи, брат', attachment=attachment)
                        elif msg == '!спортмастер' or re.match(patterns['pattern_sportmaster'], msg):
                            attachment = random.choice(loyality_cards['sportmaster'])
                            send_msg(id, text='держи, брат', attachment=attachment)

                        ##############################################################################
                        
                        elif re.match(patterns['pattern_erjan'], msg):  # ищет вопрос ержану
                            if number < 351:
                                send_msg(id, 'да')
                            if 350 < number < 701:
                                send_msg(id, 'нет')
                            if 700 < number < 751:
                                send_msg(id, 'мне поебать')
                            if 750 < number < 801:
                                send_msg(id, 'суета')
                            if 800 < number < 821:
                                send_msg(id, 'один раз не пидорас')
                            if 820 < number < 851:
                                send_msg(id, 'узнаешь')
                            if 850 < number < 856:
                                send_msg(id, 'я больше не работаю')
                            if 855 < number < 866:
                                send_msg(id, 'Я, блять, в своём познании настолько преисполнился, \
                                    что я как будто бы уже 100 триллионов миллиардов лет, блять,\
                                    проживаю на триллионах и триллионах таких же планет, понимаешь?\
                                    Как эта Земля. Мне уже этот мир абсолютно понятен, и я здесь ищу\
                                    только одного: покоя, умиротворения и вот этой гармонии от слияния \
                                    с бесконечно вечным.')
                            if 865 < number < 876:
                                send_msg(id, 'Как вам сказать… \
                                    Я прожила довольно долгую жизнь… \
                                    Ибрагим вам что-нибудь говорит?\
                                    Прекрасное имя. Аллах акбар. \
                                    Я прошла афганскую войну. И я желаю всем мужчинам пройти ее.\
                                    Мужчина определяется делом, а не словом.\
                                    И если я ношу кандибобер на голове, это не значит,\
                                    что я женщина или балерина')
                            if 875 < number < 901:
                                send_msg(id, 'отвечаю')
                            if 900 < number < 916:
                                send_msg(id, 'Ахахах, насмешил. Гуляй')
                            if 915 < number < 941:
                                send_msg(id, 'по-любому, езжи')
                            if 940 < number < 955:
                                send_msg(id, 'встану - ты ляжешь')

                        elif re.match(patterns['pattern_days_left_to_season'], msg) or msg == '!сезон':
                            season_left_days(id)

                        elif re.match(patterns['pattern_understand'], msg) and number < 300:  # не понял
                            send_msg(id, 'поймешь')

                        elif re.match(patterns['pattern_hui'], msg):  # ержана послали нахуй?
                            send_msg(id, 'Сам нахуй иди')

                        elif re.match(patterns['pattern_rso'], msg):  # любим рсо
                            send_msg(id, 'Я люблю РСО 🏳️‍🌈 🏳️‍🌈 🏳️‍🌈')

                        elif re.match(patterns['pattern_veseloe'], msg):  # Веселое? нет блин грустное
                            send_msg(id, 'Нет блин грустное')

                        elif (msg == 'Да' or msg == 'да' or msg == 'ДА') and number < 150:
                            send_msg(id, 'Манда')

                        elif (msg == 'Нет' or msg == 'нет' or msg == 'НЕТ') and number < 150:
                            send_msg(id, 'Пидора ответ')

                        elif msg == 'Ержан, сделай гифку':
                            send_gif(id, event)

                        elif msg == 'Ержан, шакализируй' or msg == 'Ержан, шакал':
                            send_shakal(id, event)

                        elif msg == 'Ержан, ультрашакал':
                            send_ultrashakal(id, event)

                        elif msg == 'Ержан, пиши диплом':
                            send_photo(id, 'photo-202528897_457239141')

                        elif msg == '!восход' or msg == '!рассвет':
                            send_msg(id, time_of_sunrise())

                        elif msg == '!заход' or msg == '!закат':
                            send_msg(id, time_of_sunset())

                        elif msg == '!время':
                            current_time = dt.datetime.now()
                            current_time = current_time.strftime('%H:%M')
                            send_msg(id, current_time)

                        elif msg == 'один раз':  # no comments
                            send_msg(id, 'не пидорас')
                except Exception as e:
                    print(e)

    except Exception:
        send_msg(1, 'Сервер перезагрузился')
