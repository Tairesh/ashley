from typing import List
import random

import googlesearch
from telebot.types import Message

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Google(Action):

    FUNNY_EXAMPLES = [
        "how to kidnap a loli",
        "жывтоне чочо упячка!!!",
        "а как какать?",
        "почему путин краб",
        "анекдот про пупу и лупу",
        "чё там у хохлов?",
    ]

    def is_not_flood(self) -> bool:
        return True

    def get_description(self) -> str:
        return "поиск в гугле"

    def get_keywords(self) -> List[str]:
        return [
            "загугли",
        ]

    def get_cmds(self) -> List[str]:
        return ["google", "g"]

    def get_name(self) -> str:
        return emoji.SEARCH + " Google"

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith("/"):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(self.FUNNY_EXAMPLES)
                self.bot.reply_to(
                    message,
                    f"Пример использования команды:\n`/{cmd} {req}`",
                    parse_mode="Markdown",
                )
                return
        else:
            if message.reply_to_message and message.reply_to_message.text:
                keyword = message.reply_to_message.text
            else:
                self.bot.reply_to(
                    message,
                    "Эту команду пока можно использовать только в ответ на другое сообщение.",
                )
                return

        try:
            url = next(googlesearch.search(keyword, stop=1))
            self.bot.reply_to(message, url)
        except StopIteration:
            self.bot.send_sticker(
                message.chat.id, stickers.FOUND_NOTHING, message.message_id
            )
