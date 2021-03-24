from typing import List

from telebot.types import Message, Chat, User

from ashlee import emoji, constants, utils
from ashlee.action import Action


class Subscribe(Action):

    def get_description(self) -> str:
        return 'подписать чат на RSS-ленту'

    def get_name(self) -> str:
        return emoji.INFO + ' RSS'

    def get_cmds(self) -> List[str]:
        return ['subscribe']

    def get_keywords(self) -> List[str]:
        return []

    def _can_subscribe(self, chat: Chat, admin: User):
        if admin.id in constants.ADMINS:
            return True

        member = self.bot.get_chat_member(chat.id, admin.id)
        if member.can_restrict_members or member.status in {"creator", "administrator"}:
            return True

        return False

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

        if not self._can_subscribe(message.chat, message.from_user):
            self.bot.reply_to(message, f"{emoji.CANCEL} Только админы могут управлять подписками чата!")
            return

        url = utils.get_keyword(message)
        if not url:
            self.bot.reply_to(message, "Пример использования команды:\n`/subscribe https://link.to/rss`",
                              parse_mode='Markdown')
            return

        d = utils.feed_parse(url)
        if not d:
            self.bot.reply_to(message, f"{emoji.SAD} Не могу распарсить RSS-ленту по этой ссылке!")
            return

        title = d['feed']['title'] if 'title' in d['feed'] else url
        if self.db.add_subscribe(message.chat.id, url, title):
            for entry in d['entries']:
                self.db.save_subscribe_post(message.chat.id, entry['id'])
            self.bot.reply_to(message, f"{emoji.CHECK} Подписка на <b>{utils.escape(title)}</b> активирована!",
                              parse_mode='HTML')
        else:
            self.bot.reply_to(message,
                              f"{emoji.CANCEL} Подписка на <b>{utils.escape(title)}</b> уже существует в этом чате!",
                              parse_mode='HTML')
