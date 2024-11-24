import os
import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from logger import logname
from routers import service, voice_to_text, mem, weather, download_video


async def main_polling() -> None:
    print(f'Path to log: {os.getcwd()}/{logname}')
    print('Start polling...')

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(
        service.router,
        voice_to_text.router,
        mem.router,
        weather.router,
        download_video.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main_polling())
