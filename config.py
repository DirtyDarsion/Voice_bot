import os
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN = os.getenv('ADMIN')
TIKTOK_VERIFY = os.getenv('TIKTOK_VERIFY')

logging.basicConfig(level=logging.DEBUG,
                    filename="voice_bot.log",
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def add_log(def_name, message=None, log_level=2, info=''):
    if message:
        user = f'{message.from_user.username}({message.from_user.id}) '
        if message.chat.type == 'group':
            chat = f'in "{message.chat.title}"({message.chat.id}) '
        else:
            chat = ''
        text = f' text: "{message.text}"'
    else:
        user, chat, text = '', '', ''

    if info:
        info = f' info: {info}'

    text = f'{user}{chat}def: {def_name}{text}{info}'

    match log_level:
        case 1:
            logging.debug(text)
        case 2:
            logging.info(text)
        case 3:
            logging.warning(text)
        case 4:
            logging.error(text)
        case 5:
            logging.critical(text)
