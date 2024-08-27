import os
import speech_recognition
import soundfile
# from pydub import AudioSegment

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

    # Change format to wav
    data, samplerate = soundfile.read(path)
    soundfile.write(new_path, data, samplerate)

    # Get text in wav
    r = speech_recognition.Recognizer()

    with speech_recognition.AudioFile(new_path) as file:
        audio = r.record(file)
        r.adjust_for_ambient_noise(file)

    os.remove(new_path)
    os.remove(path)
    return r.recognize_google(audio, language="ru-RU")


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
