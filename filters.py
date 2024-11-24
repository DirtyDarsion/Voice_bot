from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import ADMIN


class ItsMe(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN


class ItsUrl(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[:8] == 'https://'


class Text(BaseFilter):
    def __init__(self, text: Union[str], ignore_case: Union[bool] = True):
        if text:
            self.text = text
        else:
            self.text = ''
        self.ignore_case = ignore_case

    async def __call__(self, message: Message) -> bool:
        if self.ignore_case:
            if message.text:
                text = message.text
            else:
                text = ''
            return text.lower() == self.text.lower()
        else:
            return message.text == self.text
