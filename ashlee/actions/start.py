from typing import List, Optional

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Start(Action):
    def get_description(self) -> Optional[str]:
        return None

    def get_name(self) -> str:
        return emoji.INFO + ' Start'

    def get_cmds(self) -> List[str]:
        return ['start']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, f"{emoji.GOODBYE} Привет! Меня зовут Эшли, я умный бот-помощник.\n"
                                   f"Полный список моих команд доступен по команде /help")
