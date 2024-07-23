import os
import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from routers import service, voice_to_text, mem, weather


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(
    service.router,
    voice_to_text.router,
    mem.router,
    weather.router,
)


async def main() -> None:
    print(f'Path to log: {os.getcwd()}/voice_bot.log')
    print('Start polling...')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
