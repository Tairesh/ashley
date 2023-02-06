from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Debug(Action):
    def is_not_flood(self) -> bool:
        return True

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.ERROR + " Debug"

    def get_cmds(self) -> List[str]:
        return ["debug"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    @Action.only_master
    def call(self, message: Message):
        if message.reply_to_message:
            text = str(message.reply_to_message)
            for part in utils.chunks(text, 3000):
                self.bot.reply_to(
                    message, f"<code>{utils.escape(part)}</code>", parse_mode="HTML"
                )
        else:
            chat_db = self.db.get_chat(message.chat.id)
            chat_tg = self.bot.get_chat(message.chat.id)
            self.bot.reply_to(
                message,
                f"Chat in DB: "
                f"<code>{utils.escape(str(chat_db.__dict__)) if chat_db else 'None'}</code>\n\n"
                f"Chat in TG: <code>{utils.escape(str(chat_tg))}</code>",
                parse_mode="HTML",
            )
