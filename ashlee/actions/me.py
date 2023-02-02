from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Me(Action):

    def get_description(self) -> str:
        return '/me из IRC'

    def get_name(self) -> str:
        return emoji.INFO + ' Me'

    def get_cmds(self) -> List[str]:
        return ['me']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = utils.get_keyword(message)
        if keyword:
            self.bot.send_message(message.chat.id,
                                  f"<b>* {utils.user_name(message.from_user, prefer_username=True)}</b> {keyword}",
                                  parse_mode='html')
            try:
                self.bot.delete_message(message.chat.id, message.message_id)
            except ApiException:
                pass
