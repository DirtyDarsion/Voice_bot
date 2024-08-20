import os
import speech_recognition
from pydub import AudioSegment

from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters.command import Command

from filters import Text
from logger import add_log

router = Router()


'''
Если бот есть в чате, то можно ответить на голосовое сообщение фразой "вася текст"
и бот ответит текстом из сообщения.
Также бот сообщает, если в сообщении нет гс
'''


def voice_to_text(path) -> str:
    new_path = path[:-3] + 'wav'

    # Read mp3
    audio_file = AudioSegment.from_file(path)

    # Cut the audio track if it is longer than 90 seconds
    audio_len = audio_file.duration_seconds
    count = int(audio_len // 90 + (1 if audio_len % 90 else 0))
    output = ''

    # Get text in wav
    r = speech_recognition.Recognizer()
    for i in range(count):
        temp_audio = audio_file[90000 * i:90000 * (i + 1)]
        temp_audio.export(new_path, format="wav")
        with speech_recognition.AudioFile(new_path) as file:
            audio = r.record(file)
            r.adjust_for_ambient_noise(file)
            test = r.recognize_google(audio, language="ru-RU")
            output += test

        os.remove(new_path)

    os.remove(path)
    return output


@router.message(F.voice)
@router.message(Command('text'))
@router.message(Text('вася текст'))
async def get_text_from_voice(message: Message, bot: Bot) -> None:
    add_log('get_text_from_voice', message)
    if not message.voice:
        if not message.reply_to_message:
            await message.answer('Перешлите сообщение с прикрепленным аудио.')
            return
        elif not message.reply_to_message.voice:
            await message.answer('В вашем сообщении нет аудиофайла.')
            return

    try:
        if message.voice:
            file_id = message.voice.file_id
        else:
            file_id = message.reply_to_message.voice.file_id

        file = await bot.get_file(file_id)
        file_path = file.file_path
        local_path = f'voices/{message.chat.id}{message.message_id}.mp3'
        await bot.download_file(file_path, local_path)

        temp_message = await message.reply('Ожидайте...')
        text = voice_to_text(local_path)

        await temp_message.edit_text(text)
    except TypeError or AttributeError:
        await message.answer('Произошла ошибка при обработке файла.')
