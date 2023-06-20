import os
import soundfile as sf
import speech_recognition as speech_rec


def voice_to_text(path):
    # Change format to wav
    data, samplerate = sf.read(path)
    sf.write('voices/temp.wav', data, samplerate)

    # Get text in wav
    new_path = 'voices/temp.wav'
    r = speech_rec.Recognizer()

    with speech_rec.AudioFile(new_path) as file:
        audio = r.record(file)
        r.adjust_for_ambient_noise(file)

    os.remove(path)
    os.remove(new_path)

    return r.recognize_google(audio, language="ru-RU")
