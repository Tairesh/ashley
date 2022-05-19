import subprocess
from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Wordle(Action):
    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ROBOT + ' Wordle'

    def get_cmds(self) -> List[str]:
        return ['wordle']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        keyword = utils.get_keyword(message)
        if not keyword:
            return

        result = subprocess.run(['bin/wordle_simulator', keyword], stdout=subprocess.PIPE)
        self.bot.reply_to(
            message,
            result.stdout.decode('UTF-8'),
            parse_mode='markdownv2'
        )
