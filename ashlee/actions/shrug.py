from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Shrug(Action):

    def get_description(self) -> str:
        return '¯\\_(ツ)_/¯'

    def get_name(self) -> str:
        return emoji.QUESTION + ' ¯\\_(ツ)_/¯'

    def get_cmds(self) -> List[str]:
        return ['shrug']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, '¯\\_(ツ)_/¯')
