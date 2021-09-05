from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Donate(Action):

    TEXT = '''PayPal: https://paypal.me/tairesh
DonationAlerts: https://www.donationalerts.com/r/tairesh
Visa: 4274320052232272
Sberbank: `+79826151298`
YooMoney: https://sobe.ru/na/ashleybot
Monero: `4A2CkxBUVNGDSNb94FhTkpexG3evMpeVWJ4tsBDy4TLXiqTQ1Jh1CVCHUojYzHbgad7cmBphtxKW8eRVorvK5FPu4K8UhaB`
or text me @tairesh'''

    def get_description(self) -> str:
        return "реквизиты для донатов"

    def get_name(self) -> str:
        return emoji.INFO + ' Donate'

    def get_cmds(self) -> List[str]:
        return ['donate']

    def get_keywords(self) -> List[str]:
        return ['донат']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        self.bot.reply_to(message, self.TEXT, parse_mode="Markdown")
