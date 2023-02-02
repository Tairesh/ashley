from os import listdir
from os.path import join, isfile
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Updatelemons(Action):
    def get_name(self) -> str:
        return emoji.LEMON

    def get_cmds(self) -> List[str]:
        return ["update_lemons"]

    def get_keywords(self) -> List[str]:
        return []

    def get_description(self) -> str:
        return ""

    @Action.only_master
    def call(self, message: Message):
        files = [
            f
            for f in listdir("./res/lemons")
            if isfile(join("./res/lemons", f)) and f.endswith(".jpg")
        ]
        self.db.insert_lemons(files)

        self.bot.reply_to(message, "Лимоны обновлены")
