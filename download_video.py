import random
from urllib.parse import urlparse
from pytube import YouTube
from pytube import exceptions
from TikTokApi import TikTokApi

from config import add_log, TIKTOK_VERIFY

FILENAME = 'temp.mp4'


def download_youtube_video(url):
    add_log('download_youtube_video', log_level=1, info=f'start, URL: {url}')
    yt = YouTube(url)
    add_log('download_youtube_video', log_level=1, info=f'pytube object retrieved')
    if yt.length > 300:
        add_log('download_youtube_video', log_level=1, info=f'video length more 5 min, return')
        return {
            'success': False,
            'reason': 'Слишком большое видео',
        }
    else:
        add_log('download_youtube_video', log_level=1, info=f'start download video')

        try:
            yt.streams.filter(mime_type="video/mp4").get_highest_resolution().download(filename=FILENAME)
            add_log('download_youtube_video', log_level=1, info=f'video downloaded, return')
            return {
                'success': True,
                'file': FILENAME,
            }

        except exceptions.RegexMatchError:
            add_log('download_youtube_video', log_level=4, info=f'download error: RegexMatchError, return')
            return {'success': False,
                    'reason': 'Сбой в модуле загрузки YouTube'}


def download_tiktok_video(url):
    add_log('download_tiktok_video', log_level=1, info=f'start, URL: {url}')
    did = str(random.randint(10000, 999999999))
    api = TikTokApi(custom_verify_fp=TIKTOK_VERIFY, use_test_endpoints=True, custom_device_id=did)
    add_log('download_tiktok_video', log_level=1, info=f'load TikTokApi')

    video = api.video(url=url)
    add_log('download_tiktok_video', log_level=1, info=f'get video')

    video_data = video.bytes()
    add_log('download_tiktok_video', log_level=1, info=f'format video')

    with open(FILENAME, "wb") as out_file:
        add_log('download_tiktok_video', log_level=1, info=f'download video')
        out_file.write(video_data)
        add_log('download_tiktok_video', log_level=1, info=f'success')

    return {
        'success': True,
        'file': FILENAME,
    }


def download_video(url):
    add_log('download_video', log_level=1, info=f'start work, URL: {url}')
    url_parse = urlparse(url)

    if url_parse.netloc.endswith('youtube.com'):
        add_log('download_video', log_level=1, info=f'in URL defined Youtube')
        return download_youtube_video(url)
    elif url_parse.netloc.endswith('tiktok.com'):
        add_log('download_video', log_level=1, info=f'in URL defined TikTok')
        return download_tiktok_video(url)
    else:
        add_log('download_video', log_level=1, info=f'URL undefined, return')
        return {'success': False,
                'reason': 'Неизвестный URL. Бот работает с TikTok и YouTube'}
