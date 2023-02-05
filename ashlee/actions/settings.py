from typing import List, Optional

from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Chat,
    User,
    CallbackQuery,
)

from ashlee import emoji, constants
from ashlee.action import Action
from ashlee.database import ChatSettings


class Settings(Action):
    def is_not_flood(self) -> bool:
        return True

    def get_description(self) -> str:
        return "настройки работы бота в чате"

    def get_name(self) -> str:
        return emoji.INFO + " Settings"

    def get_cmds(self) -> List[str]:
        return ["settings"]

    def get_keywords(self) -> List[str]:
        return ["настройки"]

    def get_callback_start(self) -> Optional[str]:
        return "settings:"

    def _get_chat_text_and_keyboard(self, chat_settings: ChatSettings):
        def enabled(val):
            return f"{emoji.CHECK} Включено" if val else f"{emoji.CANCEL} Выключено"

        def switch(val):
            return "Включить" if not val else "Выключить"

        text = (
            "Настройки чата:\n"
            f"{emoji.STRAWBERRY} Порнография: {enabled(chat_settings.enabled_porn)}\n"
            f"{emoji.LGBT} Аниме: {enabled(chat_settings.enabled_anime)}\n"
            f"{emoji.WRITE} Бредогенератор: {enabled(chat_settings.enabled_replies)}\n"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{emoji.STRAWBERRY} Порнография: {emoji.REPEAT} {switch(chat_settings.enabled_porn)}",
                        callback_data="settings:porn",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{emoji.LGBT} Аниме: {emoji.REPEAT} {switch(chat_settings.enabled_anime)}",
                        callback_data="settings:anime",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{emoji.WRITE} Бредогенератор: {emoji.REPEAT} {switch(chat_settings.enabled_replies)}",
                        callback_data="settings:replies",
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"[ {emoji.CANCEL} Закрыть настройки ]",
                        callback_data="settings:cancel",
                    )
                ],
            ]
        )
        return text, keyboard

    def _is_admin(self, user: User, chat: Chat):
        if user.id in constants.ADMINS:
            return True

        member = self.bot.get_chat_member(chat.id, user.id)
        if member.can_restrict_members or member.status in {"creator", "administrator"}:
            return True

        return False

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        chat_id = message.chat.id
        if chat_id == message.from_user.id:
            self.bot.reply_to(
                message, f"{emoji.ERROR} Эта команда работает только в групповых чатах!"
            )
            return

        if not self._is_admin(message.from_user, message.chat):
            return

        chat_settings = self.db.get_chat_settings(chat_id)
        if chat_settings is None:
            self.db.add_chat_settings(chat_id)
            chat_settings = self.db.get_chat_settings(chat_id)
        text, keyboard = self._get_chat_text_and_keyboard(chat_settings)
        self.bot.reply_to(message, text, reply_markup=keyboard)

    def btn_pressed(self, call: CallbackQuery):
        chat_settings = self.db.get_chat_settings(call.message.chat.id)
        key = call.data.split(":").pop()
        if key == "cancel":
            self.bot.edit_message_text(
                call.message.text, call.message.chat.id, call.message.message_id
            )
            return

        elif key == "porn":
            chat_settings.enabled_porn = not chat_settings.enabled_porn
        elif key == "anime":
            chat_settings.enabled_anime = not chat_settings.enabled_anime
        elif key == "replies":
            chat_settings.enabled_replies = not chat_settings.enabled_replies

        self.db.update_chat_settings(
            call.message.chat.id,
            chat_settings.enabled_porn,
            chat_settings.enabled_anime,
            chat_settings.enabled_replies,
        )
        text, keyboard = self._get_chat_text_and_keyboard(chat_settings)
        self.bot.edit_message_text(
            text, call.message.chat.id, call.message.message_id, reply_markup=keyboard
        )
