from typing import List

from telebot.types import Message

from ashlee import emoji, constants
from ashlee.action import Action


class Subscribes(Action):

    def get_description(self) -> str:
        return 'список RSS-лент, на которые подписан чат'

    def get_name(self) -> str:
        return emoji.INFO + ' RSS'

    def get_cmds(self) -> List[str]:
        return ['subscribes']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        # if message.chat.id == message.from_user.id:
        #     self.bot.reply_to(message, f"Эта команда работает только в групповых чатах")
        #     return

        if message.chat.id != message.from_user.id:
            chat = self.db.get_chat(message.chat.id)
            vip_chat = False
            for admin in constants.ADMINS:
                if admin in chat.users:
                    vip_chat = True
                    break
            if not vip_chat:
                self.bot.reply_to(message, "Эта команда работает только в моих любимых чатах!")
                return

        subscribes = self.db.get_subscribes(message.chat.id)
        if len(subscribes) == 0:
            self.bot.reply_to(message, "Этот чат не подписан ни на одну рассылку!")
            return

        text = "<b>Список рассылок, на которые подписан этот чат:</b>\n\n"
        for i, sub in enumerate(subscribes):
            text += f"{i+1}. <a href=\"{sub.url}\">{sub.title}</a>\n"
        self.bot.reply_to(message, text, parse_mode='HTML')
