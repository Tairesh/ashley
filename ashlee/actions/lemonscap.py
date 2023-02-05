from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Lemonscap(Action):
    def get_description(self) -> str:
        return "капитализация лимонов"

    def get_name(self) -> str:
        return emoji.LEMON + " Капитализация"

    def get_cmds(self) -> List[str]:
        return ["lemons_cap", "lemonscap"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        used, total = self.db.get_sum_lemons()
        self.bot.reply_to(
            message,
            f"Общее число лимонов в сети: <b>{total} {emoji.LEMON}</b>\n"
            f"Имеет владельцев: <b>{used} {emoji.LEMON}</b>\n"
            f"Список лимонов доступных для покупки: /free_lemons",
            parse_mode="HTML",
        )
