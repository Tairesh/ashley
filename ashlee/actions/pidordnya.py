import random
from datetime import datetime
from typing import List

from telebot.types import Message

from ashlee import emoji, utils, constants
from ashlee.action import Action


class Pidordnya(Action):

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.pidors = {}

    def get_description(self) -> str:
        return 'вычислить пидора дня'

    def get_name(self) -> str:
        return emoji.INFO + ' Пидор дня'

    def get_cmds(self) -> List[str]:
        return ['pidordnya', 'pidor_dnya']

    def get_keywords(self) -> List[str]:
        return ['пидор дня', 'пидора дня', 'кто сегодня пидор']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if not message.chat or message.chat.id == message.from_user.id:
            self.bot.reply_to(message, "Эта команда работает только в чатах")
            return

        now = datetime.now()
        key = f"{message.chat.id}:{now.year}-{now.month}-{now.day}"
        if key in self.pidors:
            winner = self.pidors[key]
            self.bot.reply_to(message, f"Пидор дня сегодня уже определён, это {utils.user_name(winner)}!")
            return

        chat = self.db.get_chat(message.chat.id)
        vip_chat = False
        for admin in constants.ADMINS:
            if admin in chat.users:
                vip_chat = True
                break
        if not vip_chat:
            self.bot.reply_to(message, "Эта команда работает только в моих любимых чатах!")
            return

        users = self.db.get_users(chat.users)
        winner = random.choice(users)
        self.pidors[key] = winner
        self.db.update_user_lemons(winner.id, winner.lemons + 1)
        self.bot.reply_to(message, f"Пидор дня сегодня {utils.user_name(winner, True)}! "
                                   f"Он получает {emoji.LEMON} в награду!")
