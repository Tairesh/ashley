import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from ashlee import constants
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
    def get_name(self) -> str: pass

    # List of command strings that trigger the action
    @abstractmethod
    def get_cmds(self) -> List[str]: pass

    # List of keywords that are natural language action triggers
    @abstractmethod
    def get_keywords(self) -> List[str]: pass

    def get_callback_start(self) -> Optional[str]:
        return None

    def btn_pressed(self, call: CallbackQuery):
        pass

    @abstractmethod
    def get_description(self) -> str: pass

    # Executed logic
    @abstractmethod
    def call(self, message: Message): pass

    # Execute logic after the action is loaded
    def after_loaded(self): pass

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, message: Message):
            chat_id = message.chat.id
            try:
                self.tgb.bot.send_chat_action(chat_id=chat_id, action='typing')
            except Exception as ex:
                logging.error(f"{ex} - {message}")

            return func(self, message)
        return _send_typing_action

    @classmethod
    def send_uploading_photo(cls, func):
        def _send_uploading_photo_action(self, message: Message):
            chat_id = message.chat.id
            try:
                self.tgb.bot.send_chat_action(chat_id=chat_id, action='upload_photo')
            except Exception as ex:
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
