from aiogram import Bot, Router
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters import Text
from logger import add_log
from weather_data.data_shape import update_user, get_user_data, get_data, search_city


router = Router()


class User(StatesGroup):
    city = State()


# Функция формирования и отправки сообщения с информацией
async def send_news(user_id, bot: Bot) -> None:
    data = get_data(user_id)
    
    forecasts_text = ''
    if data['forecasts']:
        for i in data['forecasts']:
            forecasts_text += f"{i['date']}: ☀{i['day']}°C - 🌒 {i['night']}°C\n\n\n"

    text = f"Температура в <b>{data['city']}</b>: <b>{data['temp_fact']}°C</b>, ощущается <b>{data['feels_like']}°C</b>\n" \
           f"{data['condition_fact']}\n\n" \
           f"{forecasts_text}" \
           f"Доллар: <b>{data['usd']}</b>{data['usd_changes']}\nЕвро: <b>{data['eur']}</b>{data['eur_changes']}\n\n" \
           f"Время: <b>{data['time']}</b> <i>{data['date']}</i>\n\n" \
           f"Для выбора другого города введите /setcity"
    photo = FSInputFile(f"weather_data/images/{data['photo']}.jpg")

    await bot.send_photo(user_id, photo=photo, caption=text, parse_mode='HTML')


@router.message(Command('weather'))
@router.message(Text('вася погода'))
async def send_weather(message: Message, bot: Bot) -> None:
    add_log('send_weather', message)

    db_user = get_user_data(message.from_user.id)
    if db_user:
        await send_news(message.from_user.id, bot)
    else:
        await message.answer('У вас не задан город, введите команду /setcity')


@router.message(Command('setcity'))
async def send_setcity(message: Message, state: FSMContext) -> None:
    add_log('send_setcity', message)

    await state.set_state(User.city)
    db_user = get_user_data(message.from_user.id)

    if db_user:
        text = f"Ваш город: <b>{db_user['city']}</b>\n" \
               f"Часовой пояс: <b>{db_user['timezone']}</b>\n\n" \
               f"Введите название нового города:"
    else:
        text = "Введите название города:"

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )


@router.message(User.city)
async def city_chosen(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    data = await state.get_data()
    await state.clear()

    obj = search_city(data['city'])
    if obj:
        if obj['region'] is None:
            region = ''
        else:
            region = ', ' + obj['region']

        text = f"Вы выбрали: <b>{obj['city']}{region}</b>\n\n" \
               f"<i>Для смены города введите</i> /setcity"

        update_user(
            tg_id=message.from_user.id,
            city=obj['city'],
            timezone=obj['timezone'],
            lat=obj['lat'],
            lon=obj['lon']
        )
        await message.answer(text, parse_mode='HTML')
    else:
        await message.answer(f"Такого города нет, попробуйте еще раз: /setcity или /start")
