from urllib.parse import urlparse
from pytube import YouTube

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


def download_video(url):
    url_parse = urlparse(url)

    if url_parse.netloc.endswith('youtube.com'):
        return download_youtube_video(url)
    else:
        return {'success': False,
                'reason': 'Неизвестный URL'}
