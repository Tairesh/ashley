from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Help(Action):

    def get_description(self) -> str:
        return "список команд"

    def get_name(self) -> str:
        return emoji.INFO + ' Help'

    def get_cmds(self) -> List[str]:
        return ['help']

    def get_keywords(self) -> List[str]:
        return ['помощь']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        text = f"{emoji.INFO} *Вот что я умею:*\n\n"
        for action in self.tgb.actions:
            if action.get_description():
                text += ', '.join(map(lambda c: '/' + c, action.get_cmds())) + ' — ' + action.get_description() + '\n'
        self.bot.reply_to(message, text, parse_mode="Markdown")
