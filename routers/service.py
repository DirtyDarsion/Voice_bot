from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from filters import ItsMe, Text
from logger import add_log, logname

router = Router()


@router.message(Command('start'))
async def start(message: Message) -> None:
    add_log('start', message)

    await message.answer('Напиши "Вася команды"')


# Отослать админу последние 30 строчек кода
@router.message(Command('log'), ItsMe())
async def send_log(message: Message) -> None:
    add_log('get_log', message)
    with open(f'{logname}', 'r') as log:
        text = log.readlines()
        answer = text[-30:]
        message_text = ''.join(answer)
        message_text += f'\nВсего строк в логе: <b>{len(text)}</b>'
        await message.reply(message_text, parse_mode='HTML')


# Отослать адммину логфайл
@router.message(Command('logfile'), ItsMe())
async def send_log(message: Message) -> None:
    add_log('get_logfile', message)
    await message.reply_document(open(f'{logname}', 'rb'))


# Помощь
@router.message(Command('help'))
@router.message(Text('вася команды'))
async def start(message) -> None:
    add_log('start', message)

    await message.answer('Команды бота:\n'
                         '- Вася текст или /text - перевести в текст прикрепленное аудио\n'
                         '- Вася мем или /mem - отправить голосовые отрывки из мемов\n'
                         '- Вася погода или /weather - получить актуальные данные о погоде и валюте')
