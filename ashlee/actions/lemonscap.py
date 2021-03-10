from time import time
from typing import List

from telebot.types import Message

from ashlee import emoji, lemons, utils
from ashlee.action import Action


class Lemonscap(Action):

    def get_description(self) -> str:
        return 'капитализация лимонов'

    def get_name(self) -> str:
        return emoji.LEMON + ' Капитализация'

    def get_cmds(self) -> List[str]:
        return ['lemons_cap', 'lemonscap']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        lemons_count = self.db.get_sum_lemons()
        price = lemons.get_price(lemons_count)
        self.bot.reply_to(message,
                          f"Общее число лимонов в сети: <b>{lemons_count} {emoji.LEMON}</b>\n"
                          f"Стоимость DOGE в рублях: <b>{lemons.cache['doge_price']:.2f}</b> ₽ "
                          f"<i>(обновлено {utils.human_delta_t(time() - lemons.cache['updated_at'])})</i>\n\n"
                          f"Текущая стоимость {emoji.LEMON}: <b>{price}</b> ₽",
                          parse_mode='HTML')
