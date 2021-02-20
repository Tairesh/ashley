from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Ping(Action):

    def get_description(self) -> str:
        return 'проверить работу бота'

    def get_name(self) -> str:
        return emoji.INFO + ' Ping'

    def get_cmds(self) -> List[str]:
        return ['ping']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, 'Понг!')
