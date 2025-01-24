import os
import re

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import FSInputFile

from video_load_data.inst import download_iqsaved
# from video_load_data.youtube import download_savefrom
from filters import ItsUrl
from logger import add_log

router = Router()


@router.message(Command('video'))
async def video_help(message):
    add_log('video')

    await message.answer('Отправь ссылку на видео для загрузки')


@router.message(ItsUrl())
async def get_url(message):
    url = message.text.strip()
    add_log('get_video_url', message)

    temp_message = await message.answer(f'Ожидайте...')

    if re.search(r'^https://.*(instagram|ig).com', url):
        video_data = download_iqsaved(url)
    elif re.search(r'^https://.*(youtube).com', url):
        await temp_message.edit_text('В данные момент загрузка с YouTube не работает.')
        return
    #     video_data = download_savefrom(url)
    else:
        video_data = {
            'file': False,
            'error': 'Формат ссылки неизвестен, попробуйте другой'
        }

    print(video_data)

    if video_data['status'] == 'ok':
        file_path = video_data['file']
        exp = file_path.split('.')[-1]
        video = FSInputFile(file_path, filename=f'vasya_video.{exp}')
        await temp_message.delete()
        await message.answer_video(video)
        os.remove(file_path)
    elif video_data['status'] == 'large_file':
        await temp_message.edit_text(f'Вес файла превышает допустимый для загрузки(<b>{video_data['size']}</b>)',
                                     parse_mode='HTML')
        # но его можно скачать по ссылке:\n{video_data['link']}
    elif video_data['status'] == 'error':
        await temp_message.edit_text(video_data['error_text'])
    else:
        await temp_message.edit_text('Непредвиденная ошибка')
