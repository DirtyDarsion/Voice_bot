import os
import soundfile
import speech_recognition

from aiogram import Router, Bot, F
from aiogram.types import Message

from filters import Text
from logger import add_log

router = Router()


'''
Если бот есть в чате, то можно ответить на голосовое сообщение фразой "вася текст"
и бот ответит текстом из сообщения.
Также бот сообщает, если в сообщении нет гс
'''


def voice_to_text(path) -> str:
    # Change format to wav
    data, samplerate = soundfile.read(path)
    soundfile.write('voices/temp.wav', data, samplerate)

    # Get text in wav
    new_path = 'voices/temp.wav'
    r = speech_recognition.Recognizer()

    with speech_recognition.AudioFile(new_path) as file:
        audio = r.record(file)
        r.adjust_for_ambient_noise(file)

    os.remove(path)
    os.remove(new_path)

    return r.recognize_google(audio, language="ru-RU")


@router.message(Text('вася текст'))
async def get_text_from_voice(message: Message, bot: Bot, main_def=True) -> None:
    add_log('get_text_from_voice', message)
    if main_def:
        if not message.reply_to_message:
            await message.answer('Перешлите сообщение с прикрепленным аудио.')
            return
        elif not message.reply_to_message.voice:
            await message.answer('В вашем сообщении нет аудиофайла.')
            return

    try:
        if main_def:
            file_id = message.reply_to_message.voice.file_id
        else:
            file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        local_path = 'voices/temp.mp3'
        await bot.download_file(file_path, local_path)

        temp_message = await message.reply('Ожидайте...')
        text = voice_to_text(local_path)

        await temp_message.edit_text(text)
    except TypeError and AttributeError:
        await message.answer('Произошла ошибка при обработке файла.')


@router.message(F.voice)
async def get_text_from_voice2(message: Message, bot: Bot) -> None:
    await get_text_from_voice(message, bot, main_def=False)
