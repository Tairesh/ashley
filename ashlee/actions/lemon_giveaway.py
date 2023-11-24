import datetime
import random
from os.path import join
from typing import List, Optional

from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ashlee import emoji, utils, stickers
from ashlee.action import Action
from ashlee.actions.lemons import Lemons


class Lemon_giveaway(Action):
    last_giveaway = 0

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.LEMON + " Бесплатный лимон"


    def get_cmds(self) -> List[str]:
        return ["lemon_giveaway"]

    def get_keywords(self) -> List[str]:
        return ["дай лимон"]

    def get_callback_start(self) -> Optional[str]:
        return "take_lemon:"

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.chat.id != utils.PEEROJOQUE_CHAT_ID:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO)
            return

        if datetime.date.day == self.last_giveaway:
            self.bot.reply_to(message, "Сегодня больше бесплатных лимонов не будет, приходите завтра! " + emoji.LEMON)
            return

        self.last_giveaway = datetime.date.day

        free_lemons = self.db.get_free_lemons()
        lemon = random.choice(free_lemons)
        self.bot.send_photo(
            message.chat.id,
            open(join(Lemons.DIR, lemon.image), "rb"),
            f"{emoji.LEMON} LMN #{lemon.id}\n<b>Free</b>",
            reply_to_message_id=message.message_id,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{emoji.LEMON} Забрать лимон",
                            callback_data=f"take_lemon:{lemon.id}",
                        )
                    ]
                ],
                1,
            ),
        )

    def btn_pressed(self, call: CallbackQuery):
        lemon_id = int(call.data.split(":")[1])
        lemon = self.db.get_lemon(lemon_id)
        if lemon.owner_id is not None:
            return

        self.db.update_lemon_owner(lemon.id, call.from_user.id)
        self.bot.delete_message(call.message.chat.id, call.message.message_id)
        self.bot.send_photo(
            call.message.chat.id,
            open(join(Lemons.DIR, lemon.image), "rb"),
            f"{emoji.LEMON} LMN #{lemon.id}\n"
            + (
                f"PWNED by {utils.user_name(self.db.get_user(call.from_user.id), True, True, True, 'HTML')}"
            ),
            parse_mode="HTML",
        )
