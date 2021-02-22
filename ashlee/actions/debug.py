from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Debug(Action):

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ERROR + ' Debug'

    def get_cmds(self) -> List[str]:
        return ['debug']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        if message.reply_to_message:
            text = str(message.reply_to_message)
            for part in utils.chunks(text, 3000):
                self.bot.reply_to(message, f"<code>{part}</code>", parse_mode='HTML')
        else:
            chat = self.bot.get_chat(message.chat.id)
            self.bot.reply_to(message, f"Chat in DB: <code>{str(self.db.get_chat(message.chat.id).__dict__)}</code>\n\n"
                                       f"Chat in TG: <code>{str(chat)}</code>", parse_mode='HTML')
