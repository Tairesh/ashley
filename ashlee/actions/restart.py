import os
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Restart(Action):

    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.REPEAT + ' Restart'

    def get_cmds(self) -> List[str]:
        return ['restart']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        self.bot.reply_to(message, 'OK, master')
        os.system('sudo systemctl restart ashlee.service')
