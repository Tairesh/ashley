from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Del(Action):

    def get_description(self) -> str:
        return 'удалить сообщение бота'

    def get_name(self) -> str:
        return emoji.CANCEL + ' Del'

    def get_cmds(self) -> List[str]:
        return ['del']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    def call(self, message: Message):
        if message.reply_to_message and message.reply_to_message.from_user.id == self.tgb.me.id:
            try:
                self.bot.delete_message(message.chat.id, message.reply_to_message.message_id)
            except ApiException:
                pass
