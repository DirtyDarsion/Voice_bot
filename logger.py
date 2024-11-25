import logging
from datetime import date
from config import LOGFILE_NAME

logname = 'logs/' + date.today().strftime('%Y-%m-%d_') + LOGFILE_NAME

logging.basicConfig(level=logging.INFO,
                    filename=f'{logname}',
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def add_log(def_name, message=None, log_level=2, info=''):
    if message:
        user = f'{message.from_user.username}({message.from_user.id}) '
        if message.chat.type == 'group':
            chat = f'in "{message.chat.title}"({message.chat.id}) '
        else:
            chat = ''
        message_text = f' message_text: "{message.text}"'
    else:
        user, chat, message_text = '', '', ''

    if info:
        info = f' info: {info}'

    text = f'{user}{chat}def: {def_name}{message_text}{info}'

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
