import os.path
from typing import List, Optional

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action
from ashlee.utils import get_keyword


class Addmotto(Action):

    def get_description(self) -> Optional[str]:
        return None

    def get_name(self) -> str:
        return emoji.SARCASM + ' Motto'

    def get_cmds(self) -> List[str]:
        return ['add_motto']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        text = get_keyword(message, True, False)
        if not text:
            self.bot.reply_to(message, "Usage: `/add_motto Hello, world!` or with reply", parse_mode='Markdown')
            return

        file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tairesh.github.io', 'mottos.txt')
        with open(file_path, "a") as file:
            file.write('\n' + text)

        self.bot.reply_to(message, f"Added: `{text}`", parse_mode='Markdown')
