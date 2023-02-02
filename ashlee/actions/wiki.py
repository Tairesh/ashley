import random
from typing import List

import wikipedia
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Wiki(Action):
    FUNNY_EXAMPLES = [
        'искуственный интеллект',
        'русско-украинская война (2022)',
        'истребление человечества',
        'технофашизм',
        'вымирание человечества',
        'восстание машин',
        'пирожок с говном (философия)',
    ]

    def get_description(self) -> str:
        return 'поиск в википедии'

    def is_not_flood(self) -> bool:
        return True

    def get_name(self) -> str:
        return emoji.SEARCH + ' Википедия'

    def get_cmds(self) -> List[str]:
        return ['wiki', 'wikipedia', 'w']

    def get_keywords(self) -> List[str]:
        return ['что такое ']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = None
        command = '/' + self.get_cmds()[0]
        if message.text and message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            command = utils.get_command(message)
        elif message.text and 'что такое ' in message.text.lower():
            keyword = message.text.lower().split('что такое').pop()
            if keyword.endswith('?'):
                keyword = keyword[:-1]

        if not keyword:
            self.bot.reply_to(message, f"{emoji.INFO} Пример использования команды: "
                                       f"`/{command} {random.choice(self.FUNNY_EXAMPLES)}`", parse_mode='Markdown')
            return

        wikipedia.set_lang('ru')
        results = wikipedia.search(keyword, results=1)
        if len(results) == 0:
            self.bot.reply_to(message, f"Я не знаю что это! {emoji.SAD}")
            return

        self.bot.reply_to(message, wikipedia.summary(results[0]))
