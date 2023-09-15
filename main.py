import os
import nest_asyncio

import asyncio
import aioschedule
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher.filters import Command, Text, IDFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import NetworkError, RetryAfter, TelegramAPIError

from config import add_log, TOKEN, ADMIN
from voice_to_text import voice_to_text
from download_video import download_video

nest_asyncio.apply()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dir_set = CallbackData('dir', 'user_id', 'dir')
voice_set = CallbackData('voi', 'user_id', 'voice')

db = {}


@dp.message_handler(Command('start'))
async def start(message):
    add_log('start', message)

    await message.answer('Напиши Вася')


@dp.message_handler(Command('help'))
async def start(message):
    add_log('start', message)

    await message.answer('Команды:\n'
                         '- Вася видео;\n'
                         '- Вася текст;\n'
                         '- Вася логфайл;\n'
                         '- Вася лог;\n'
                         '- Вася')


@dp.message_handler(Text(startswith='вася видео', ignore_case=True))
async def get_video(message):
    add_log('get_video', message)

    data = message.text.split()
    if len(data) != 3:
        add_log('get_video', message, log_level=1, info='bad format')
        await message.answer('Неверный формат!\nДля загрузки видео введите "Вася видео <ссылка на видео>"')
        return

    temp_message = await message.answer('Работаю')

    url = data[2]

    add_log('get_video', message, log_level=1, info='load "download_video"')
    ans = download_video(url)
    add_log('get_video', message, log_level=1, info=f'download_video response: {ans}')

    if ans['success']:
        await temp_message.edit_text(message.from_user.first_name)
        await bot.send_video(message.chat.id, open(ans['file'], 'rb'))
        add_log('get_video', message, log_level=1, info=f'video sent successful')
        os.remove(ans['file'])
    else:
        await temp_message.edit_text(ans['reason'])


@dp.message_handler(Text(startswith='вася текст', ignore_case=True))
async def get_text_from_voice(message):
    add_log('get_text_from_voice', message)

    try:
        file_id = message.reply_to_message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        local_path = 'voices/temp.mp3'
        await bot.download_file(file_path, local_path)

        temp_message = await message.reply('Работаю')
        text = voice_to_text(local_path)

        await temp_message.edit_text(text)
    except TypeError and AttributeError:
        await message.answer('Произошла ошибка.')


@dp.message_handler(Text(startswith='логфайл', ignore_case=True), IDFilter(ADMIN))
async def send_log(message):
    add_log('get_logfile', message)
    await message.reply_document(open('voice_bot.log', 'rb'))


@dp.message_handler(Text(startswith='лог', ignore_case=True), IDFilter(ADMIN))
async def send_log(message):
    add_log('get_log', message)
    with open('voice_bot.log', 'r') as log:
        text = log.readlines()
        answer = text[-30:]
        message_text = ''.join(answer)
        await message.reply(message_text)


@dp.message_handler(Text(startswith='вася', ignore_case=True))
async def get_voice(message):
    add_log('get_voice', message)

    user_id = message.from_user.id
    categories = os.listdir('voices')

    keyboard = InlineKeyboardMarkup()
    for item in categories:
        keyboard.add(InlineKeyboardButton(item, callback_data=dir_set.new(user_id=user_id, dir=item)))

    await message.answer('Выбери мем', reply_markup=keyboard)


@dp.callback_query_handler(dir_set.filter())
async def choose_voice(call: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']

    if call.from_user.id != int(user_id):
        await call.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(call.id)
    else:
        dir_name = callback_data['dir']
        db[user_id] = {'dir': dir_name}

        path = 'voices/' + dir_name
        voices = sorted(os.listdir(path))

        keyboard = InlineKeyboardMarkup()
        for item in voices:
            item_cut = item[:-4]
            keyboard.add(InlineKeyboardButton(item_cut, callback_data=voice_set.new(user_id=user_id, voice=item)))

        await call.message.edit_text(dir_name, reply_markup=keyboard)


@dp.callback_query_handler(voice_set.filter())
async def send_voice(call: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']

    if call.from_user.id != int(user_id):
        await call.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(call.id)
    else:
        dir_name = db[user_id]['dir']
        voice = callback_data['voice']
        path = f'voices/{dir_name}/{voice}'

        await call.message.delete()
        await bot.send_voice(call.message.chat.id, InputFile(path))


@dp.errors_handler(exception=[NetworkError, RetryAfter, TelegramAPIError])
async def error_intercept(update: types.Update):
    add_log('error_intercept', 'перехвачена ошибка', log_level=4)

    return True


def log_cleaner():
    log_length = 3000

    with open('voice_bot.log', 'r') as file:
        text = file.readlines()

    length = len(text)
    if length > log_length:
        with open('voice_bot.log', 'w') as file:
            file.writelines(text[-log_length:])

    return length


async def scheduler():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(86400)
        len_log = log_cleaner()
        add_log('log_cleaner', info=f'length = {len_log}')


async def on_startup(_):
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
    )
