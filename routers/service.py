from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from filters import ItsMe, Text

from logger import add_log
from config import LOGFILE_NAME

router = Router()


@router.message(Command('start'))
async def start(message: Message):
    add_log('start', message)

    await message.answer('Напиши "Вася команды"')


# Отослать админу последние 30 строчек кода
@router.message(Command('log'), ItsMe())
async def send_log(message: Message):
    add_log('get_log', message)
    with open(LOGFILE_NAME, 'r') as log:
        text = log.readlines()
        answer = text[-30:]
        message_text = ''.join(answer)
        message_text += f'\nВсего строк в логе: <b>{len(text)}</b>'
        await message.reply(message_text, parse_mode='HTML')


# Отослать адммину логфайл
@router.message(Command('logfile'), ItsMe())
async def send_log(message: Message):
    add_log('get_logfile', message)
    await message.reply_document(open(LOGFILE_NAME, 'rb'))


# Аналог /help
@router.message(Text('вася команды'))
async def start(message):
    add_log('start', message)

    await message.answer('Команды бота:\n'
                         '- Вася текст - перевести в текст прикрепленное аудио, можно отправить просто гс.')

    # await message.answer('Команды бота:\n'
    #                      '- Вася видео <ссылка на видео> - загрузка видео из других источников в диалог;\n'
    #                      '- Вася текст - перевести в текст прикрепленное аудио, можно отправить просто гс;\n'
    #                      '- Вася мем.')
