from os import getcwd
from os.path import join
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Freelemons(Action):
    DIR = join(getcwd(), "res", "lemons")

    def get_name(self) -> str:
        return "Ничейные лимоны"

    def get_description(self) -> str:
        return ""

    def get_cmds(self) -> List[str]:
        return ["free_lemons", "freelemons"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(
            message,
            ", ".join(
                f"{emoji.LEMON} LMN #{lemon.id}" for lemon in self.db.get_free_lemons()
            )
            + "\n\nПосмотреть лимон по ID: `/lemon 1` покажет LMN #1",
            parse_mode="Markdown",
        )
