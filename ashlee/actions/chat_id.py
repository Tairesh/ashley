from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Chat_id(Action):
    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ERROR + " Get chat id"

    def get_cmds(self) -> List[str]:
        return ["chat_id"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, f"Chat id is: {message.chat.id}")
