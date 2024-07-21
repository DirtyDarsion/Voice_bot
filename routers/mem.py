import os

from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from logger import add_log
from filters import Text

router = Router()


class DirSet(CallbackData, prefix='dir'):
    user_id: int
    dir: str


class VoiceSet(CallbackData, prefix='voice'):
    user_id: int
    voice: str


db = {}


@router.message(Text('вася мем', ignore_case=True))
async def get_voice(message: Message):
    add_log('get_voice', message)

    user_id = message.from_user.id
    categories = os.listdir('voices')

    keyboard = InlineKeyboardBuilder()
    for item in categories:
        keyboard.add(
            InlineKeyboardButton(
                text=item,
                callback_data=DirSet(user_id=user_id, dir=item).pack(),
            )
        )
    keyboard.adjust(1)

    await message.answer('Выбери мем', reply_markup=keyboard.as_markup())


@router.callback_query(DirSet.filter())
async def choose_voice(callback: CallbackQuery, callback_data: DirSet, bot: Bot):
    user_id = callback_data.user_id

    if callback.from_user.id != int(user_id):
        await callback.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(callback.id)
    else:
        dir_name = callback_data.dir
        db[user_id] = {'dir': dir_name}

        path = 'voices/' + dir_name
        voices = sorted(os.listdir(path))

        keyboard = InlineKeyboardBuilder()
        for item in voices:
            item_cut = item[:-4]
            keyboard.add(
                InlineKeyboardButton(
                    text=item_cut,
                    callback_data=VoiceSet(user_id=user_id, voice=item).pack(),
                )
            )
        keyboard.adjust(1)

        await callback.message.edit_text(dir_name, reply_markup=keyboard.as_markup())


@router.callback_query(VoiceSet.filter())
async def send_voice(callback: CallbackQuery, callback_data: VoiceSet, bot: Bot):
    user_id = callback_data.user_id

    if callback.from_user.id != int(user_id):
        await callback.answer('Сообщение вызвано другим пользователем')
        await bot.answer_callback_query(callback.id)
    else:
        dir_name = db[user_id]['dir']
        voice = callback_data.voice
        path = f'voices/{dir_name}/{voice}'

        await callback.message.delete()
        await bot.send_voice(callback.message.chat.id, FSInputFile(path))
