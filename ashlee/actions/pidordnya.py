from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Pidordnya(Action):

    def get_description(self) -> str:
        return 'вычислить пидора дня'

    def get_name(self) -> str:
        return emoji.INFO + ' Пидор дня'

    def get_cmds(self) -> List[str]:
        return ['pidordnya', 'pidor_dnya']

    def get_keywords(self) -> List[str]:
        return ['пидор дня', 'пидора дня', 'кто сегодня пидор']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, f"Пидор дня сегодня {utils.user_name(message.from_user)}!")
