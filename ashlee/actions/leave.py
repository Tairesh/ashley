from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji, constants, stickers
from ashlee.action import Action


class Leave(Action):
    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.CANCEL + " Выйти из чата"

    def get_cmds(self) -> List[str]:
        return ["leave"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.chat.id == message.from_user.id:
            self.bot.reply_to(
                message, f"{emoji.ERROR} Эта команда работает только в групповых чатах!"
            )
            return

        if message.from_user.id not in constants.ADMINS:
            return

        try:
            self.bot.leave_chat(message.chat.id)
        except ApiException:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO, message.message_id)
