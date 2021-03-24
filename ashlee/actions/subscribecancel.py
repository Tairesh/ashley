from typing import List

from telebot.types import Message, Chat, User, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ashlee import emoji, constants
from ashlee.action import Action


class Subscribecancel(Action):

    NUMBERS_EMOJI = {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
        10: "🔟",
    }

    def get_description(self) -> str:
        return 'отписать чат от RSS-ленты'

    def get_name(self) -> str:
        return emoji.INFO + ' RSS'

    def get_cmds(self) -> List[str]:
        return ['subscribe_cancel', 'subscribes_cancel', 'subscribecancel', 'subscribescancel',
                'cancel_subscribe', 'cancel_subscribes', 'cancelsubscribe', 'cancelsubscribes']

    def get_keywords(self) -> List[str]:
        return []

    def get_callback_start(self) -> str:
        return 'sc:'

    def _can_subscribe(self, chat: Chat, admin: User):
        if admin.id in constants.ADMINS:
            return True

        member = self.bot.get_chat_member(chat.id, admin.id)
        if member.can_restrict_members or member.status in {"creator", "administrator"}:
            return True

        return False

    def btn_pressed(self, call: CallbackQuery):
        chat_id = call.message.chat.id
        self.bot.send_chat_action(chat_id, 'typing')
        url = call.data[3:]
        if url == 'cancel':
            text = '\n'.join(call.message.text.split('\n')[:-1]) + '\n<i>(Отмена подписки отменена)</i>'
            self.bot.edit_message_text(text, chat_id, call.message.message_id,
                                       reply_markup=None, parse_mode='HTML')
        else:
            self.db.delete_subscribe(chat_id, url)
            self.bot.reply_to(call.message.reply_to_message, f"{emoji.CHECK} Подписка на {url} успешно удалена!")
            self.bot.delete_message(chat_id, call.message.message_id)

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        # if message.chat.id == message.from_user.id:
        #     self.bot.reply_to(message, f"Эта команда работает только в групповых чатах")
        #     return

        if not self._can_subscribe(message.chat, message.from_user):
            self.bot.reply_to(message, f"{emoji.CANCEL} Только админы могут управлять подписками чата!")
            return

        subscribes = self.db.get_subscribes(message.chat.id)
        if len(subscribes) == 0:
            self.bot.reply_to(message, "Этот чат не подписан ни на одну рассылку!")
            return

        markup = InlineKeyboardMarkup(row_width=5)
        btns = []
        text = "<b>Список рассылок, на которые подписан этот чат:</b>\n\n"
        for i, sub in enumerate(subscribes):
            text += f"{i+1}. <a href=\"{sub.url}\">{sub.title}</a>\n"
            btns.append(InlineKeyboardButton(self.NUMBERS_EMOJI[i+1] if i < 10 else str(i+1),
                                             callback_data='sc:' + sub.url))
        markup.add(*btns)
        markup.add(InlineKeyboardButton(f"{emoji.CANCEL} Отмена", callback_data='sc:cancel'))
        text += "\n<b>Выберите какую из рассылок удалить:</b>"
        self.bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')
