from typing import List, Optional

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Reload(Action):

    def get_description(self) -> Optional[str]:
        return None

    def get_name(self) -> str:
        return emoji.LEMON + ' Reload commands'

    def get_cmds(self) -> List[str]:
        return ['reload']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        self.tgb.reload_actions()
        self.bot.reply_to(message, f"{emoji.INFO} {len(self.tgb.actions)} команд перезагружено")
