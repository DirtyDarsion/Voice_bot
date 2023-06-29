import os
from TikTokApi import TikTokApi


url_video = 'https://vt.tiktok.com/ZSLSA9eRR/'


def download_tiktok(url):
    with TikTokApi() as api:
        video = api.video(url=url)
        print(video.info())


download_tiktok(url_video)
