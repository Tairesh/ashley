from typing import List

from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from ashlee import emoji, utils
from ashlee.action import Action


class Duel(Action):
    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.duels = {}

    def get_description(self) -> str:
        return "дуэль на дайсах"

    def get_name(self) -> str:
        return emoji.LEMON + " Дуэль"

    def get_cmds(self) -> List[str]:
        return ["duel"]

    def get_keywords(self) -> List[str]:
        return ["дуэль"]

    def get_callback_start(self):
        return "duel:"

    def after_loaded(self):
        @Action.save_data
        @self.bot.message_handler(
            content_types=["dice"],
            func=lambda m: not m.forward_from and m.dice and m.dice.emoji == "🎲",
        )
        def _dice_sent(message: Message):
            if message.chat.id in self.duels:
                user_id = message.from_user.id
                duel = self.duels[message.chat.id]
                if user_id in duel["r"].keys():
                    if duel["r"][user_id]:
                        self.bot.reply_to(
                            message, f"{emoji.INFO} Перебрасывать нельзя!"
                        )
                        return
                    else:
                        duel["r"][user_id] = message.dice.value
                        if all(duel["r"].values()):
                            self._duel_check(message.chat.id)

    def after_unload(self):
        for i, handler in enumerate(self.bot.message_handlers):
            if "content_types" in handler and "dice" in handler["content_types"]:
                self.bot.message_handlers.pop(i)

    def _duel_check(self, chat_id):
        duel = self.duels[chat_id]
        user1, user2 = duel["r"].keys()
        u1 = self.db.get_user(user1)
        u2 = self.db.get_user(user2)
        dice1 = duel["r"][user1]
        dice2 = duel["r"][user2]
        result1 = dice1
        result2 = dice2
        if result1 > result2:
            winner = u1
        elif result2 > result1:
            winner = u2
        else:
            self.duels[chat_id]["r"][user1] = None
            self.duels[chat_id]["r"][user2] = None
            self.bot.send_message(
                chat_id,
                f"{utils.user_name(u1, True, True)} и {utils.user_name(u2, True, True)} "
                f"у вас ничья, перебрасывайте {emoji.DICE}!",
                reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True).add(
                    emoji.DICE
                ),
            )
            return

        self.duels.pop(chat_id)
        self.bot.send_message(
            chat_id,
            "<b>Результаты:</b>\n"
            f"<i>{utils.user_name(u1)}:</i> {dice1}\n"
            f"<i>{utils.user_name(u2)}:</i> {dice2}\n"
            f"<b>Победитель:</b> {utils.user_name(winner, True)}!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )

    def btn_pressed(self, call: CallbackQuery):
        if call.data.endswith("cancel"):
            self.bot.edit_message_text(
                f"{call.message.text}\n{emoji.CANCEL} Вызов отклонён!",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=None,
            )
            return

        sender_id = int(call.data.split(":").pop())
        sender = self.db.get_user(sender_id)
        recipient_id = call.from_user.id
        self.duels[call.message.chat.id] = {"r": {sender_id: None, recipient_id: None}}

        self.bot.edit_message_text(
            f"{call.message.text}\n{emoji.CHECK} Вызов принят! ",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None,
        )
        self.bot.reply_to(
            call.message.reply_to_message,
            f"{utils.user_name(sender, True, True)} и "
            f"{utils.user_name(call.from_user, True, True)} "
            f"отправьте в чат дайсы {emoji.DICE} чтобы сразиться в кости!",
            reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True).add(emoji.DICE),
        )

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            self.bot.reply_to(
                message,
                f"{emoji.INFO} Чтобы вызвать врага на дуэль, "
                f"используйте эту команду в ответ на его сообщение!",
            )
            return
        if message.reply_to_message.from_user.is_bot:
            self.bot.reply_to(message, f"{emoji.INFO} Нельзя вызвать на дуэль бота!")
            return
        elif message.reply_to_message.from_user.id == message.from_user.id:
            self.bot.reply_to(
                message, f"{emoji.INFO} Нельзя вызвать на дуэль самого себя!"
            )
            return

        recipient = message.reply_to_message.from_user
        self.bot.reply_to(
            message.reply_to_message,
            f"{utils.user_name(recipient, True)}, вас вызывает на дуэль {utils.user_name(message.from_user)}!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{emoji.CHECK} Принять вызов",
                            callback_data=f"duel:{message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            f"{emoji.CANCEL} Отклонить вызов",
                            callback_data="duel:cancel",
                        ),
                    ]
                ]
            ),
        )
