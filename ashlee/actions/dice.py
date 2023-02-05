from typing import List, Optional

import dice
from telebot.apihelper import ApiException
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Dice(Action):
    def get_description(self) -> str:
        return "кинуть дайс"

    def get_name(self) -> str:
        return emoji.DICE + " Dice"

    def get_cmds(self) -> List[str]:
        return ["dice", "roll"]

    def get_keywords(self) -> List[str]:
        return [
            "кинь кубик",
            "кинь дайс",
            "брось кубик",
            "брось дайс",
            "брось кости",
            "кинь кости",
        ]

    def get_callback_start(self) -> Optional[str]:
        return "dice:"

    def _dice_btn(self, dice_val):
        return InlineKeyboardButton(text=dice_val, callback_data="dice:" + dice_val)

    def _dice_markup(self):
        markup = InlineKeyboardMarkup()
        markup.row(self._dice_btn("d4"), self._dice_btn("d6"), self._dice_btn("d8"))
        markup.row(self._dice_btn("d10"), self._dice_btn("d12"), self._dice_btn("d20"))
        markup.row(self._dice_btn("d100"), self._dice_btn("+1d"), self._dice_btn("-1d"))
        return markup

    def btn_pressed(self, call):
        data = call.data[5::]
        count = int(call.message.text.split(" ")[1])
        if data in {"+1d", "-1d"}:
            if data == "+1d":
                count += 1
            elif data == "-1d":
                if count == 1:
                    return
                count -= 1

            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=self._dice_markup(),
                text=f"Бросить {count} дайс:",
            )
        else:
            self.bot.send_chat_action(call.message.chat.id, "typing")
            self.try_roll_and_send(call.message.reply_to_message, str(count) + data)
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except ApiException:
                pass

    def try_roll_and_send(self, message, keyword):
        try:
            d = dice.roll(keyword)
            self.bot.reply_to(message, f"{emoji.DICE} {keyword} rolls {str(d)}")
        except dice.DiceException:
            self.bot.send_sticker(message.chat.id, stickers.CANT_DO, message.message_id)

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith("/"):
            keyword = utils.get_keyword(message)
        else:
            keyword = None

        if not keyword:
            self.bot.reply_to(
                message, "Бросить 1 дайс:", reply_markup=self._dice_markup()
            )
            return

        self.try_roll_and_send(message, keyword)
