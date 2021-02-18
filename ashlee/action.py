import logging
from abc import ABC, abstractmethod
from typing import List

from telegram import ChatAction
from telegram.ext import CommandHandler, CallbackContext

from ashlee import constants
from ashlee.telegrambot import TelegramBot


class ActionInterface(ABC):

    # List of command strings that trigger the action
    @abstractmethod
    def get_cmds(self) -> List[str]: pass

    # List of regexes that are natural language action triggers
    @abstractmethod
    def get_regexes(self) -> List[str]: pass

    # Logic that gets executed if action is triggered
    @abstractmethod
    def get_action(self, update, context): pass

    # Execute logic after the action is loaded
    def after_loaded(self):
        return None


class Action(ActionInterface, ABC):

    def __init__(self, telegram_bot: TelegramBot):
        super().__init__()

        self.tgb: TelegramBot = telegram_bot
        self.add_action()

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, update, context: CallbackContext):
            if update.message:
                chat_id = update.message.chat_id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat_id
            else:
                return func(self, update, context)

            try:
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            except Exception as ex:
                logging.error(f"{ex} - {update}")

            return func(self, update, context)
        return _send_typing_action

    @classmethod
    def save_data(cls, func):
        def _save_data(self, update, context):
            if update.message:
                usr = update.message.from_user
                cmd = update.message.text
                cht = update.message.chat
            elif update.inline_query:
                usr = update.effective_user
                cmd = update.inline_query.query[:-1]
                cht = update.effective_chat
            else:
                logging.warning(f"Can't save usage - {update}")
                return func(self, update, context)

            self.tgb.db.save_cmd(usr, cht, cmd)

            return func(self, update, context)
        return _save_data

    @classmethod
    def only_master(cls, func):
        def _only_master(self, update, context):
            if update.effective_user.id in constants.ADMINS:
                return func(self, update, context)

        return _only_master

    def add_action(self):
        self.tgb.dispatcher.add_handler(
            CommandHandler(self.get_cmds(), self.get_action))

        self.tgb.actions.append(self)

        logging.info(f"Plugin '{type(self).__name__}' added")

    def remove_action(self):
        for handler in self.tgb.dispatcher.handlers[0]:
            if isinstance(handler, CommandHandler):
                if set(handler.command) == set(self.get_cmds()):
                    self.tgb.dispatcher.handlers[0].remove(handler)
                    break

        self.tgb.actions.remove(self)

        logging.info(f"Plugin '{type(self).__name__}' removed")