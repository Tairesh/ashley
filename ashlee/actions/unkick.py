from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message, User, Chat

from ashlee import emoji, constants, stickers, utils
from ashlee.action import Action


class Unkick(Action):

    def get_description(self) -> str:
        return 'разбанить юзера в чате'

    def get_name(self) -> str:
        return emoji.CHECK + ' Разбан'

    def get_cmds(self) -> List[str]:
        return ['unkick', 'unban', 'nekick', 'razban']

    def get_keywords(self) -> List[str]:
        return ['разбань', 'разбанить']

    def _can_do(self, chat: Chat, admin: User):
        if admin.id in constants.ADMINS:
            return True

        member = self.bot.get_chat_member(chat.id, admin.id)
        if member.can_restrict_members or member.status in {"creator", "administrator"}:
            return True

        return False

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.chat.id == message.from_user.id:
            self.bot.reply_to(message, f"{emoji.ERROR} Эта команда работает только в групповых чатах!")
            return

        if not self._can_do(message.chat, message.from_user):
            return

        if not message.reply_to_message:
            self.bot.reply_to(
                message,
                f"{emoji.INFO} Чтобы разбанить пользователя, используй эту команду ответом на его сообщение!"
            )
            return

        user = message.reply_to_message.from_user

        if user.id == self.tgb.me.id:
            return

        try:
            name = utils.user_name(user, True)
            self.bot.unban_chat_member(message.chat.id, user.id)
            self.bot.reply_to(message, f"{name} был разбанен")
        except ApiException:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO, message.message_id)
