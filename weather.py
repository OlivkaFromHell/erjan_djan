import requests
import json
from datetime import datetime

text_to_emoji = {
    'снег': '🌨',
    'пасмурно': '☁',
    'небольшой снег': '🌨',
    'небольшая облачность': '🌤',  # большое солнце, маленькое облако
    'переменная облачность': '⛅',  # маленькое солнце, большое облако
    'облачно с прояснениями': '🌤',  # большое солнце, маленькое облако
    'ясно': '☀',
    'небольшой дождь': '🌧',
    'дождь': '🌧',
    'туман': '🌫'
}

def get_forecast_data():
    """send current weather and weather description"""
    api_url = 'http://api.openweathermap.org/data/2.5/forecast'
    s_city = "Санкт-Петербург"
    city_id = 0
    appid = 'a1e9cd07fa2f720fa36b7a5870f75f66'

    params = {
        'q': s_city,
        'appid': appid,
        'units': 'metric',
        'lang': 'ru',
        'cnt': 9,
    }
    res = requests.get(api_url, params=params)

    return res.json()

def convert_temp_descript(data):
    temperature = round(data['main']['temp'])
    weather_description = data['weather'][0]['description']
    if weather_description in text_to_emoji:
        weather_description_emoji = text_to_emoji[weather_description]
    elif 'туман' in weather_description:
        weather_description_emoji = text_to_emoji['туман']
    else:
        weather_description_emoji = weather_description

    return [temperature, weather_description_emoji, data['clouds']['all']]

def time_of_sunrise(data=get_forecast_data()):
    sunrise = datetime.fromtimestamp(data['city']['sunrise'])
    if sunrise.minute // 10 == 0:
        sunrise_time = f"🌅  {sunrise.hour}:0{sunrise.minute}"
    else:
        sunrise_time = f"🌅  {sunrise.hour}:{sunrise.minute}"

    return sunrise_time

def time_of_sunset(data=get_forecast_data()):
    sunset = datetime.fromtimestamp(data['city']['sunset'])
    if sunset.minute // 10 == 0:
        sunset_time = f"🌇  {sunset.hour}:0{sunset.minute}"
    else:
        sunset_time = f"🌇  {sunset.hour}:{sunset.minute}"

    return sunset_time

def current_weather():
    """send current weather and weather description"""
    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    s_city = "Санкт-Петербург"
    city_id = 0
    appid = 'a1e9cd07fa2f720fa36b7a5870f75f66'

    params = {
        'q': s_city,
        'appid': appid,
        'units': 'metric',
        'lang': 'ru',
        'cnt': 9,
    }
    res = requests.get(api_url, params=params)

    data = res.json()
    template = 'Сейчас на улице {}°С | {} \nОблачность: {}%'
    temperature = round(data['main']['temp'])
    weather_description = data['weather'][0]['description']
    if weather_description in text_to_emoji:
        weather_description_emoji = text_to_emoji[weather_description]
    elif 'туман' in weather_description:
        weather_description_emoji = text_to_emoji['туман']
    else:
        weather_description_emoji = weather_description
    ans = template.format(temperature, weather_description_emoji, data['clouds']['all'])

    return ans

def for_day_weather():
    """send current weather and weather description"""
    api_url = 'http://api.openweathermap.org/data/2.5/forecast'
    s_city = "Санкт-Петербург"
    city_id = 0
    appid = 'a1e9cd07fa2f720fa36b7a5870f75f66'

    params = {
        'q': s_city,
        'appid': appid,
        'units': 'metric',
        'lang': 'ru',
        'cnt': 9,
    }
    res = requests.get(api_url, params=params)

    data = res.json()

    sunrise_time = time_of_sunrise(data)

    sunset_time = time_of_sunset(data)

    sun_time = '\n' + sunrise_time + '\n' + sunset_time

    ans = 'Доброе утро!\n'

    
    daily_morning = data['list'][0]
    template = 'Сейчас на улице {}°С | {}\n'
    tem = convert_temp_descript(daily_morning)
    ans += template.format(tem[0], tem[1])

    daily_afternoon = data['list'][2]
    template = '🕒 {}°С | {} | {}%\n'
    tem = convert_temp_descript(daily_afternoon)
    ans += template.format(tem[0], tem[1], tem[2])

    daily_evening = data['list'][3]
    template = '🕕 {}°С | {} | {}%\n'
    tem = convert_temp_descript(daily_evening)
    ans += template.format(tem[0], tem[1], tem[2])

    daily_night = data['list'][6]
    template = '🌃 {}°С | {} | {}%\n'
    tem = convert_temp_descript(daily_night)
    ans += template.format(tem[0], tem[1], tem[2])

    ans += sun_time

    return ans

if __name__ == '__main__':
    print(time_of_sunrise())
