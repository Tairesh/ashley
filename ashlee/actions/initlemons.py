from os import listdir
from os.path import join, isfile
import random
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Initlemons(Action):

    def get_name(self) -> str:
        return emoji.LEMON

    def get_cmds(self) -> List[str]:
        return ['init_lemons']

    def get_keywords(self) -> List[str]:
        return []

    def get_description(self) -> str:
        return ''

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        self.db.truncate_lemons()
        self.db.update_user_lemons(self.bot.get_me().id, 0)
        files = [f for f in listdir("./res/lemons") if isfile(join("./res/lemons", f)) and f.endswith('.jpg')]
        self.db.insert_lemons(files)

        free_lemons = self.db.get_all_lemons()
        random.shuffle(free_lemons)

        counter = 0
        for user in self.db.get_all_users():
            for i in range(user.lemons):
                lemon = free_lemons.pop()
                self.db.update_lemon_owner(lemon.id, user.id)
                counter += 1

        self.bot.reply_to(message, f"Распределены нфт-лимоны: {counter}")
