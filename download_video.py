import random
import string
from urllib.parse import urlparse
from pytube import YouTube
from TikTokApi import TikTokApi

from vars import TIKTOK_VERIFY

FILENAME = 'temp.mp4'


def download_youtube_video(url):
    yt = YouTube(url)
    if yt.length > 300:
        return {
            'success': False,
            'reason': 'Слишком большое видео',
        }
    else:
        yt.streams.filter(mime_type="video/mp4").get_highest_resolution().download(filename=FILENAME)
        return {
            'success': True,
            'file': FILENAME,
        }


def download_tiktok_video(url):
    api = TikTokApi(custom_verify_fp=TIKTOK_VERIFY, use_test_endpoints=True)

    video = api.video(url=url)
    print(video.id)

    video_data = video.bytes()
    with open(FILENAME, "wb") as out_file:
        out_file.write(video_data)

    return {
        'success': True,
        'file': FILENAME,
    }


def download_video(url):
    url_parse = urlparse(url)

    if url_parse.netloc.endswith('youtube.com'):
        return download_youtube_video(url)
    elif url_parse.netloc.endswith('tiktok.com'):
        return download_tiktok_video(url)
    else:
        return {'success': False,
                'reason': 'Неизвестный URL'}
