from typing import List

from telebot.types import Message

from ashlee import emoji, pepe, utils
from ashlee.action import Action


class Forget(Action):

    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.CANCEL + ' Forget'

    def get_cmds(self) -> List[str]:
        return ['forget']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        if not message.reply_to_message or not message.reply_to_message.text \
                or message.reply_to_message.from_user.id != self.tgb.me.id:
            return

        trigrams = pepe.remove_all_trigrams(self.tgb.redis, message.reply_to_message.text)
        text = "These keys have been successfully forgotten: " + ", ".join(['->'.join(t) for t in trigrams])
        for t in utils.chunks(text, 3000):
            self.bot.reply_to(message, t)
