import re
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
    def call(self, message: Message):
        keyword = utils.get_keyword(message).lower().replace('ё', 'е').replace('\n', '').strip()
        if not keyword:
            return self.bot.reply_to(
                message,
                "Нужно указать слово для угадывания, например `/wordle тоска`",
                parse_mode='markdownv2'
            )

        keyword = re.sub(r"[^А-яёЁ]", "", keyword)

        result = subprocess.run(['bin/wordle_simulator', keyword], stdout=subprocess.PIPE)
        self.bot.reply_to(
            message,
            result.stdout.decode('UTF-8'),
            parse_mode='markdownv2'
        )
