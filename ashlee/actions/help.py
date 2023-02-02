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
        text = f"{emoji.INFO} <b>Вот что я умею:</b>\n\n"
        pairs = []
        for action in self.tgb.actions:
            if action.get_description():
                pairs.append((action.get_cmds()[0], action.get_description()))

        pairs.sort(key=lambda p: p[0])

        for cmd, desc in pairs:
            text += f"/{cmd} — <b>{desc}</b>\n"
        self.bot.reply_to(message, text, parse_mode="HTML")
