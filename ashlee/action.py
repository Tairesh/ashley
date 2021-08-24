import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ashlee import constants, emoji
from ashlee.database import Database


class Action(ABC):

    def __init__(self, telegram_bot):
        super().__init__()

        self.tgb = telegram_bot
        self.tgb.actions.append(self)
        self.bot: TeleBot = telegram_bot.bot
        self.db: Database = telegram_bot.db

    # Name of action
    @abstractmethod
    def get_name(self) -> str:
        pass

    # List of command strings that trigger the action
    @abstractmethod
    def get_cmds(self) -> List[str]:
        pass

    # List of keywords that are natural language action triggers
    @abstractmethod
    def get_keywords(self) -> List[str]:
        pass

    def get_callback_start(self) -> Optional[str]:
        return None

    def btn_pressed(self, call: CallbackQuery):
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    # Executed logic
    @abstractmethod
    def call(self, message: Message):
        pass

    # Execute logic after the action is loaded
    def after_loaded(self):
        pass

    # Execute logic after the action is unloaded
    def after_unload(self):
        pass

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, message: Message):
            chat_id = message.chat.id
            try:
                self.tgb.bot.send_chat_action(chat_id=chat_id, action='typing')
            except ApiException as ex:
                logging.error(f"{ex} - {message}")

            return func(self, message)
        return _send_typing_action

    @classmethod
    def send_uploading_photo(cls, func):
        def _send_uploading_photo_action(self, message: Message):
            chat_id = message.chat.id
            try:
                self.tgb.bot.send_chat_action(chat_id=chat_id, action='upload_photo')
            except ApiException as ex:
                logging.error(f"{ex} - {message}")

            return func(self, message)
        return _send_uploading_photo_action

    @classmethod
    def save_data(cls, func):
        def _save_data(self, message: Message):
            if message.text:
                text = message.text
            else:
                text = message.content_type
            self.tgb.db.save_cmd(message.from_user, message.chat, text)
            return func(self, message)
        return _save_data

    @classmethod
    def only_master(cls, func):
        def _only_master(self, message: Message):
            if message.from_user.id in constants.ADMINS:
                return func(self, message)

        return _only_master


class SudoAction(Action, ABC):

    @abstractmethod
    def _get_label(self) -> str:
        pass

    @abstractmethod
    def _get_settings_attr(self) -> str:
        pass

    @abstractmethod
    def _try_process_action(self, message: Message) -> bool:
        pass

    def btn_pressed(self, call: CallbackQuery):
        if call.data.endswith('sudo'):
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(f"{emoji.CHECK} Да", callback_data=self.get_callback_start() + 'yes'),
                InlineKeyboardButton(f"{emoji.CANCEL} Отмена", callback_data=self.get_callback_start() + 'cancel'),
            ]])
            self.bot.edit_message_text(
                f"{call.message.text}\nВы действительно хотите потратить {emoji.LEMON} и отправить запрещёнку?",
                call.message.chat.id, call.message.message_id, reply_markup=kb
            )
            return
        elif call.data.endswith('cancel'):
            self.bot.edit_message_text(f"{emoji.ERROR} {self._get_label()} запрещено в этом чате!",
                                       call.message.chat.id, call.message.message_id, reply_markup=None)
            return
        elif call.data.endswith('yes'):
            if not call.message.reply_to_message:
                return
            user = self.db.get_user(call.message.reply_to_message.from_user.id)
            if user.lemons > 0:
                self.bot.edit_message_text(f"{emoji.ERROR} {self._get_label()} запрещено в этом чате!\n"
                                           f"Но тем у кого много лимонов закон не писан...",
                                           call.message.chat.id, call.message.message_id, reply_markup=None)
                if self._try_process_action(call.message.reply_to_message):
                    self.db.update_user_lemons(user.id, user.lemons - 1)
            else:
                self.bot.edit_message_text(f"{emoji.ERROR} {self._get_label()} запрещено в этом чате!",
                                           call.message.chat.id, call.message.message_id, reply_markup=None)

    @Action.save_data
    def call(self, message: Message):
        settings = self.db.get_chat_settings(message.chat.id)
        if settings and not settings.__getattribute__(self._get_settings_attr()):
            user = self.db.get_user(message.from_user.id)
            if user.lemons > 0:
                kb = InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"{emoji.LEMON} Потратить лимон и всё равно отправить",
                                         callback_data=self.get_callback_start() + 'sudo')
                ]])
            else:
                kb = None
            self.bot.reply_to(message, f"{emoji.ERROR} {self._get_label()} запрещено в этом чате!", reply_markup=kb)
            return

        self._try_process_action(message)
