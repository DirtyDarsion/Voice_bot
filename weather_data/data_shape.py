import psycopg2
import requests
import json
from datetime import datetime, timedelta

from config import YANDEX_API_KEY, DB_HOST, DB_NAME, DB_USER, DB_PASS


with open('weather_data/cities.json', 'r', encoding='UTF-8') as f:
    cities = json.load(f)

# Перевод всех состояний погоды с Яндекса https://yandex.ru/dev/weather/doc/dg/concepts/forecast-test.html
conditions = {
    'clear': 'Ясно',
    'partly-cloudy': 'Малооблачно',
    'cloudy': 'Облачно',
    'overcast': 'Пасмурно',
    'drizzle': 'Морось',
    'light-rain': 'Небольшой дождь',
    'rain': 'Дождь',
    'moderate-rain': 'Умеренно',
    'heavy-rain': 'Сильный',
    'continuous-heavy-rain': 'Длительный',
    'showers': 'Ливень',
    'wet-snow': 'Мокрый снег',
    'light-snow': 'Небольшой снег',
    'snow': 'Снег',
    'snow-showers': 'Снегопад',
    'hail': 'Град',
    'thunderstorm': 'Гроза',
    'thunderstorm-with-rain': 'Дождь',
    'thunderstorm-with-hail': 'Гроза',
}

# Названия картинок для всех состояний погоды
condition_photo = {
    'clear': 'clear',
    'partly-cloudy': 'partly-cloudy',
    'cloudy': 'cloudy',
    'overcast': 'overcast',
    'drizzle': 'rain',
    'light-rain': 'rain',
    'rain': 'rain',
    'moderate-rain': 'rain',
    'heavy-rain': 'rain',
    'continuous-heavy-rain': 'rain',
    'showers': 'rain',
    'wet-snow': 'snow',
    'light-snow': 'snow',
    'snow': 'snow',
    'snow-showers': 'snow',
    'hail': 'hail',
    'thunderstorm': 'thunderstorm',
    'thunderstorm-with-rain': 'thunderstorm-rain',
    'thunderstorm-with-hail': 'thunderstorm-rain',
}


# Изменение данных о пользователе в ДБ
def update_user(tg_id, city, timezone, lat, lon) -> None:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor()

    cursor.execute(f"SELECT tg_id FROM users WHERE tg_id = {tg_id};")
    answer = cursor.fetchall()

    if answer:
        cursor.execute(f"UPDATE users "
                       f"SET city = '{city}', timezone = '{timezone}', lat = {lat}, lon = {lon} "
                       f"WHERE tg_id = {tg_id};")
    else:
        cursor.execute(f"INSERT INTO users (tg_id, city, timezone, lat, lon) "
                       f"VALUES ({tg_id}, '{city}', '{timezone}', {lat}, {lon});")
    conn.commit()
    cursor.close()
    conn.close()


# Получение данных о пользователе в ДБ
def get_user_data(tg_id) -> dict:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor()

    cursor.execute(f'SELECT tg_id, city, timezone, lat, lon FROM users WHERE tg_id = {tg_id};')
    answer = cursor.fetchall()
    cursor.close()
    conn.close()

    if answer:
        answer = answer[0]
        output = {
            'id': answer[0],
            'city': answer[1],
            'timezone': answer[2],
            'lat': answer[3],
            'lon': answer[4],
        }
    else:
        output = {}

    return output


# Фунция получения данных о погоде и валюте
def get_data(user_id) -> dict:
    user_data = get_user_data(user_id)
    # Получение данных о валюте
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        valute = response.json()['Valute']

        usd = valute['USD']['Value']
        usd_prev = valute['USD']['Previous']
        if usd > usd_prev:
            usd_changes = '⬆'
        else:
            usd_changes = '⬇'
        usd = round(usd, 2)

        eur = valute['EUR']['Value']
        eur_prev = valute['EUR']['Previous']
        if eur > eur_prev:
            eur_changes = '⬆'
        else:
            eur_changes = '⬇'
        eur = round(eur, 2)
    except requests.exceptions.JSONDecodeError:
        usd, usd_changes, eur, eur_changes = 'Ошибка' * 4

    # Получение данных о погоде
    try:
        response = requests.get(f"https://api.weather.yandex.ru/v2/informers?"
                                f"lat={user_data['lat']}&"
                                f"lon={user_data['lon']}&"
                                f"[lang=ru-RU]",
                                headers={'X-Yandex-API-Key': YANDEX_API_KEY})
        weather = response.json()

        try:
            forecasts = []
            forecasts_request = weather['forecasts'][1:]
            for i in forecasts_request:
                date = datetime.strptime(i['date'], '%Y-%m-%d')
                day_in_fc = {
                    'date': date.strftime('%d.%m'),
                    'day': i['parts']['day']['temp_avg'],
                    'night': i['parts']['night']['temp_avg']
                }
                forecasts.append(day_in_fc)
        except KeyError:
            forecasts = None

        temp_fact = weather['fact']['temp']
        feels_like = weather['fact']['feels_like']
        condition_fact = weather['fact']['condition']
        photo = condition_photo[condition_fact]
        condition_fact = conditions[condition_fact]

    except requests.exceptions.JSONDecodeError:
        temp_fact, feels_like, condition_fact = ['Ошибка соединения' for _ in range(3)]
        forecasts = None
        photo = 'error'

    # Формирование даты
    utc = int(user_data['timezone'][4:])
    tz = timedelta(hours=utc)
    dt = datetime.now() + tz

    data = {
        'city': user_data['city'],
        'time': dt.strftime('%H:%M'),
        'date': dt.strftime('%d.%m.%y'),
        'usd': usd,
        'usd_changes': usd_changes,
        'eur': eur,
        'eur_changes': eur_changes,
        'photo': photo,
        'temp_fact': temp_fact,
        'feels_like': feels_like,
        'condition_fact': condition_fact,
        'forecasts': forecasts,
    }

    return data


# Функция проверки наличия данных о городе
def search_city(name) -> str:
    for obj in cities:
        if name.lower() == obj['city'].lower():
            return obj
