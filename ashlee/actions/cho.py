import random
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Cho(Action):
    def get_description(self) -> str:
        return "чё?"

    def get_name(self) -> str:
        return emoji.QUESTION + " Чё?"

    def get_cmds(self) -> List[str]:
        return ["cho"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(
            message,
            "чё"
            + random.choice(("", "", "", "", "", "", "?", "!", "?", "!", "!!!", "...")),
        )
