from typing import List

from telebot.types import Message, ReplyKeyboardRemove

from ashlee import emoji
from ashlee.action import Action


class Clear(Action):

    def is_not_flood(self) -> bool:
        return True

    def get_description(self) -> str:
        return 'очистить чат от клавиатур'

    def get_name(self) -> str:
        return emoji.CANCEL + ' Clear'

    def get_cmds(self) -> List[str]:
        return ['clear']

    def get_keywords(self) -> List[str]:
        return ['очисти чат']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, 'Чат очищен!', reply_markup=ReplyKeyboardRemove())
