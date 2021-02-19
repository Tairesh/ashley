import logging
from abc import ABC, abstractmethod
from typing import List

from telebot.types import Message

from ashlee import constants
from ashlee.telegrambot import TelegramBot


class Action(ABC):

    def __init__(self, telegram_bot: TelegramBot):
        super().__init__()

        self.tgb: TelegramBot = telegram_bot
        self.tgb.actions.append(self)

    # Name of action
    @abstractmethod
    def get_name(self) -> str: pass

    # List of command strings that trigger the action
    @abstractmethod
    def get_cmds(self) -> List[str]: pass

    # List of keywords that are natural language action triggers
    @abstractmethod
    def get_keywords(self) -> List[str]: pass

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
    def save_data(cls, func):
        def _save_data(self, message: Message):
            self.tgb.db.save_cmd(message.from_user, message.chat, message.text)
            return func(self, message)
        return _save_data

    @classmethod
    def only_master(cls, func):
        def _only_master(self, message: Message):
            if message.from_user.id in constants.ADMINS:
                return func(self, message)

        return _only_master
