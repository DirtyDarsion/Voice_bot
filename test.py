import os
from TikTokApi import TikTokApi


url_video = 'https://vt.tiktok.com/ZSLSA9eRR/'


def download_tiktok(url):
    with TikTokApi() as api:
        video = api.video(url=url)
        video_data = video.bytes()
        with open("out.mp4", "wb") as out_file:
            out_file.write(video_data)


download_tiktok(url_video)
