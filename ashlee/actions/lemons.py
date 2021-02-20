import re

from ashlee import emoji, utils
from ashlee.action import Action


class Lemons(Action):

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        user = self.tgb.db.get_user(message.from_user.id)
        count = user.lemons
        if count == 0:
            self.tgb.bot.reply_to(message, "У тебя нет ни одного лимона!")
        else:
            self.tgb.bot.reply_to(message, f"Вот твои лимоны, {count} штук: {emoji.LEMON * count}")

    def get_keywords(self):
        return ["лимоны"]

    def get_cmds(self):
        return ["lemons"]
