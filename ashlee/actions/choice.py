import random
import re
from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Choice(Action):

    r_or = re.compile(r'\s+(или|or)\s+', flags=re.IGNORECASE)

    def get_description(self) -> str:
        return 'выбрать вариант'

    def get_name(self) -> str:
        return emoji.INFO + ' Выбрать вариант'

    def get_cmds(self) -> List[str]:
        return ['choice']

    def get_keywords(self) -> List[str]:
        return [' или ']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
        else:
            keyword = message.text
        if keyword[-1::] == '?':
            keyword = keyword[:-1:]
        if not keyword:
            self.bot.reply_to(message, "Пример использования \n`/choice быть или не быть?`", parse_mode='markdown')
            return
        variants = self.r_or.split(keyword)
        for var in variants:
            if self.r_or.search(f" {var} "):
                variants.remove(var)
        sel = random.choice(variants)
        self.bot.reply_to(message, sel)
