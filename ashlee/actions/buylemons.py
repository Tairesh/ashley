from typing import List

from telebot.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery

from ashlee import emoji, utils
from ashlee.action import Action


class Buylemons(Action):

    def get_description(self) -> str:
        return 'купить лимоны'

    def get_name(self) -> str:
        return emoji.LEMON + ' Купить'

    def get_cmds(self) -> List[str]:
        return ['buy_lemons', 'buylemons', 'buy_lemon', 'buylemon']

    def get_keywords(self) -> List[str]:
        return []

    def get_callback_start(self):
        return 'lemons'

    def after_loaded(self):
        @self.bot.pre_checkout_query_handler(lambda q: True)
        def _answer_pre_checkout_query(query: PreCheckoutQuery):
            self.bot.answer_pre_checkout_query(query.id, True)

        @self.bot.message_handler(content_types=['successful_payment'])
        def _successful_payment(message: Message):
            if message.successful_payment and message.successful_payment.invoice_payload:
                lemons = int(message.successful_payment.invoice_payload.split(':').pop())
                user = self.db.get_user(message.from_user.id)
                self.db.update_user_lemons(user.id, user.lemons + lemons)
                self.bot.reply_to(message, f"Спасибо за покупку! Теперь у тебя {user.lemons + lemons} {emoji.LEMON}")

    def btn_pressed(self, call: CallbackQuery):
        amount = call.data.split(':').pop()
        if amount != 'cancel':
            amount = int(amount)
            price = amount * 100
            self.bot.send_invoice(
                call.message.chat.id,
                f"{utils.format_number(amount, 'лимонов', 'лимон', 'лимона')} за {price} рублей",
                f'{emoji.LEMON} Лимоны абсолютно бесполезны, нет никакого смысла их покупать! '
                f'Но если очень хочется — жми кнопку.',
                f'lemons:{amount}', self.tgb.api_keys['payments_token'],
                'RUB', [LabeledPrice('Лимоны', price * 100)], "test-payment"
            )
        self.bot.delete_message(call.message.chat.id, call.message.message_id)

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.chat and message.chat.id != message.from_user.id:
            self.bot.reply_to(message, f"{emoji.INFO} Платежи работают только в личных сообщениях!")
            return
        self.bot.reply_to(message, "Сколько лимонов ты хочешь купить? Каждый лимон стоит 100 рублей.",
                          reply_markup=InlineKeyboardMarkup([[
                              InlineKeyboardButton('1 ' + emoji.LEMON, callback_data='lemons:1'),
                              InlineKeyboardButton('5 ' + emoji.LEMON, callback_data='lemons:5'),
                              InlineKeyboardButton('10 ' + emoji.LEMON, callback_data='lemons:10'),
                          ], [
                              InlineKeyboardButton(emoji.CANCEL + ' Cancel', callback_data='lemons:cancel')
                          ]]))
