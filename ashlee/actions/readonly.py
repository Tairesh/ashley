import re
from time import time
from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message, User, Chat

from ashlee import emoji, constants, stickers, utils
from ashlee.action import Action


class Readonly(Action):
    TIME_KEYS_TO_VALS = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7,
        'y': 60 * 60 * 24 * 365,
        'с': 1,
        'м': 60,
        'ч': 60*60,
        'д': 60 * 60 * 24,
        'н': 60 * 60 * 24 * 7,
        'л': 60 * 60 * 24 * 365,
    }
    r_time_interval = re.compile(r"^(\d+)\s*(s|m|h|d|w|y|с|м|ч|д|н|л|)", flags=re.IGNORECASE)

    def get_description(self) -> str:
        return 'временный ридонли'

    def get_name(self) -> str:
        return emoji.CANCEL + ' Ридонли'

    def get_cmds(self) -> List[str]:
        return ['ro']

    def get_keywords(self) -> List[str]:
        return ['ридонли']

    def _can_restrict(self, chat: Chat, admin: User):
        if admin.id in constants.ADMINS:
            return True

        member = self.bot.get_chat_member(chat.id, admin.id)
        if member.can_restrict_members or member.status in {"creator", "administrator"}:
            return True

        return False

    def _time_interval_to_sec(self, match: re.Match):
        val, key = match.groups()
        k = self.TIME_KEYS_TO_VALS[key] if key in self.TIME_KEYS_TO_VALS else 60
        return int(val) * k

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if not self._can_restrict(message.chat, message.from_user):
            return

        if not message.reply_to_message:
            return

        try:
            user = message.reply_to_message.from_user
            keyword = utils.get_keyword(message, False)
            if keyword.strip() == '':
                interval = 5*60
            else:
                match = self.r_time_interval.match(keyword)
                if match:
                    interval = self._time_interval_to_sec(match)
                else:
                    self.bot.reply_to(message, "Возможные значения: `5м` или `10 дней`", parse_mode='Markdown')
                    return
            date = round(time())+interval
            self.bot.restrict_chat_member(message.chat.id, user.id, until_date=date)
            self.bot.reply_to(message, f"{utils.user_name(user)} получил ридонли на {interval} секунд")
        except ApiException:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO, message.message_id)
