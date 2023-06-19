import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher.filters import Command, Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


dir_set = CallbackData('dir', 'user_id', 'dir')
voice_set = CallbackData('voi', 'user_id', 'voice')

db = {}


@dp.message_handler(Command('start'))
async def start(message):
    await message.answer('Напиши вася')


@dp.message_handler(Text(startswith='вася', ignore_case=True))
async def choose_dir(message):
    user_id = message.from_user.id
    categories = os.listdir('voices')

    keyboard = InlineKeyboardMarkup()
    for item in categories:
        keyboard.add(InlineKeyboardButton(item, callback_data=dir_set.new(user_id=user_id, dir=item)))

    await message.answer('Выбери мем', reply_markup=keyboard)


@dp.callback_query_handler(dir_set.filter())
async def choose_voice(call: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']
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
    dir_name = db[user_id]['dir']
    voice = callback_data['voice']
    path = f'voices/{dir_name}/{voice}'

    await call.message.delete()
    await bot.send_voice(call.message.chat.id, InputFile(path))


async def on_startup(_):
    print('Start bot!')


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        skip_updates=True,
    )
