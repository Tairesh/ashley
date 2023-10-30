import re
from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action

first_syllable = re.compile(r"([цкнгшщзхфвпрлджчсмтб]+[аоеияуюыэё]+)\w", re.UNICODE | re.IGNORECASE)


class Kal(Action):
    def is_not_flood(self) -> bool:
        return False

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.SHIT + " Кализация"

    def get_cmds(self) -> List[str]:
        return ["kal"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if not message.reply_to_message:
            self.bot.reply_to(message, "💩")
            return

        text = utils.get_text(message.reply_to_message)
        if not text:
            self.bot.reply_to(message, "💩")
            return

        words = text.split(" ")
        new_words = []
        for word in words:
            search = first_syllable.search(word)
            if not search:
                new_words.append(word)
                continue

            match = search.group(1)
            if match:
                new_words.append(word.replace(str(match), "кал", 1))

        result = " ".join(new_words)
        self.bot.reply_to(message, result)
