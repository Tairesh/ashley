import random
from time import time
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Viktordle(Action):
    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ROBOT + ' Viktordle'

    def get_cmds(self) -> List[str]:
        return ['viktordle']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = int(utils.get_keyword(message))

        day = 24 + (int(time()) - 1653073200) // (24*60*60)
        attempts = keyword if 0 < keyword else random.randint(2, 6)
        attempts_displ = attempts if attempts <= 6 else 'x'
        text = f"Игра Viktordle (RU) День #{day} {attempts_displ}/6\n\n"

        line = "⭕⭕⭕⭕⭕"
        lines = [line]
        for i in range(attempts - 1):
            line = list(line)
            for _ in range(random.randint(1, 3)):
                j = random.randint(0, 4)
                line[j] = '❌'
            lines.append(''.join(line))
        text += '\n'.join(reversed(lines)[:6])
        text += "\n\n#виктордли\n\nОтгадайте слово на  https://viktordle.nikolaev.one/"

        self.bot.reply_to(message, text)
