import os
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Redisinfo(Action):
    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.INFO + " Redis Info"

    def get_cmds(self) -> List[str]:
        return ["pepe_info", "redis_info"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        self.bot.reply_to(
            message,
            "<code>"
            + os.popen("redis-cli INFO Keyspace | grep ^db").read()
            + "</code>",
            parse_mode="html",
        )
