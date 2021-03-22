from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message, User, Chat

from ashlee import emoji, constants, stickers, utils
from ashlee.action import Action


class Kick(Action):

    def get_description(self) -> str:
        return 'кикнуть юзера из чата'

    def get_name(self) -> str:
        return emoji.CANCEL + ' Бан'

    def get_cmds(self) -> List[str]:
        return ['kick', 'ban', 'psyop']

    def get_keywords(self) -> List[str]:
        return ['забань', 'кикни', 'забанить', 'кикнуть']

    def _can_kick(self, chat: Chat, admin: User):
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
            self.bot.reply_to(message, "Эта команда работает только в групповых чатах")
            return

        if not self._can_kick(message.chat, message.from_user):
            return

        if not message.reply_to_message:
            return

        try:
            user = message.reply_to_message.from_user
            name = 'Psy-op' if message.text.startswith('/psyop') else utils.user_name(user, True)
            self.bot.kick_chat_member(message.chat.id, user.id)
            self.bot.restrict_chat_member(message.chat.id, user.id)
            self.bot.reply_to(message, f"{name} был забанен")
        except ApiException:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO, message.message_id)
