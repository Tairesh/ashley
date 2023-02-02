import random
from time import time
from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Viktordle(Action):
    MAX_ATTEMPTS = 6

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ROBOT + " Viktordle"

    def get_cmds(self) -> List[str]:
        return ["viktordle"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = utils.get_keyword(message)

        day = 24 + (int(time()) - 1653073200) // (24 * 60 * 60)
        attempts = (
            max(1, int(keyword))
            if keyword
            else random.randint(2, self.MAX_ATTEMPTS + 1)
        )
        attempts_displ = attempts if attempts <= self.MAX_ATTEMPTS else "x"
        text = (
            f"Игра Viktordle (RU) День #{day} {attempts_displ}/{self.MAX_ATTEMPTS}\n\n"
        )

        line = "⭕⭕⭕⭕⭕"
        lines = [line]
        for i in range(attempts - 1):
            line = list(line)
            for _ in range(random.randint(1, 3)):
                j = random.randint(0, 4)
                line[j] = "❌"
            lines.append("".join(line))
        text += "\n".join(list(reversed(lines))[: self.MAX_ATTEMPTS])
        text += "\n\n#виктордли\n\nОтгадайте слово на  https://viktordle.nikolaev.one/"

        self.bot.reply_to(message, text)
