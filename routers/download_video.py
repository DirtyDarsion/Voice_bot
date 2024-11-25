import os
import re

from aiogram import Router, Bot
from aiogram.filters.command import Command
from aiogram.types import FSInputFile

from video_load_data.inst import download_iqsaved
from filters import ItsUrl
from logger import add_log

router = Router()


@router.message(Command('video'))
async def video_help(message):
    add_log('video')

    await message.answer('Отправь ссылку на видео для загрузки')


@router.message(ItsUrl())
async def get_url(message, bot: Bot):
    add_log('get_video_url')
    url = message.text.strip()

    if re.search(r'^https://.*(instagram|ig).com', url):
        temp_message = await message.answer(f'Ожидайте...')
        video_data = download_iqsaved(url)
        if video_data['file']:
            file_path = video_data['file']
            exp = file_path.split('.')[-1]
            video = FSInputFile(file_path, filename=f'inst_video.{exp}')
            await temp_message.delete()
            await message.answer_video(video)
            os.remove(file_path)
        else:
            await temp_message.edit_text(f'Вес файла превышает допустимый для загрузки(<b>{video_data['size']}</b>), '
                                         f'но его можно скачать по ссылке:\n{video_data['link']}', parse_mode='HTML')
    else:
        await message.answer('Формат ссылки неизвестен, попробуйте другой')
