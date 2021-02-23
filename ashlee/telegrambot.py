import importlib
import logging
import os
import threading
from typing import Dict, List

from redis import StrictRedis
from telebot import TeleBot
from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ashlee import emoji, constants, utils, stickers
from ashlee.action import Action
from ashlee.database import Database


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class TelegramBot:

    def __init__(self, token, api_keys, db, redis, clean=False, debug=False):
        self.token: str = token
        self.api_keys: Dict[str, str] = api_keys
        self.db: Database = db
        self.redis: StrictRedis = redis
        self.clean: bool = clean
        self.debug: bool = debug
        self.actions: List[Action] = []

        self.bot: TeleBot = TeleBot(token, skip_pending=clean)
        self.me: User = self.bot.get_me()

        # Load classes in folder 'actions'
        self._load_actions()

        self.bot.add_message_handler({'function': self._handle_text_messages, 'filters': {
            'func': lambda m: m.text and not m.forward_from_chat,
            'content_types': ['text'],
        }})

        self.bot.add_callback_query_handler({'function': self._handle_callback_queries, 'filters': {}})

    # Start the bot
    def bot_start_polling(self):
        for admin in constants.ADMINS:
            self.bot.send_message(admin, emoji.INFO + ' I was restarted')

    # Go in idle mode
    def bot_idle(self):
        if self.debug:
            self.bot.polling(True)
        else:
            self.bot.infinity_polling()

    def _load_actions(self):
        threads = list()

        for _, _, files in os.walk(os.path.join('ashlee', 'actions')):
            for file in files:
                if not file.lower().endswith('.py'):
                    continue
                if file.startswith('_') or file.startswith('.'):
                    continue

                threads.append(self._load_action(file))

        # Make sure that all plugins are loaded
        for thread in threads:
            thread.join()

    @threaded
    def _load_action(self, file):
        try:
            module_name = file[:-3]
            module_path = f"ashlee.actions.{module_name}"
            module = importlib.import_module(module_path)

            action_class = getattr(module, module_name.capitalize())
            action_class(self).after_loaded()
        except Exception as ex:
            msg = f"File '{file}' can't be loaded as an action: {ex}"
            logging.warning(msg)

    def remove_action(self, module_name):
        for action in self.actions:
            if type(action).__name__.lower() == module_name.lower():
                self.actions.remove(action)
                break

    def reload_action(self, module_name):
        self.remove_action(module_name)

        try:
            module_path = f"ashlee.actions.{module_name}"
            module = importlib.import_module(module_path)

            importlib.reload(module)

            action_class = getattr(module, module_name.capitalize())
            action_class(self)
        except Exception as ex:
            msg = f"Action '{module_name.capitalize()}' can't be reloaded: {ex}"
            logging.warning(msg)
            raise ex

    # Handle all errors
    def _handle_errors(self, message, exception):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{exception} - {cls_name} - {message}")

        if message:
            self.bot.send_sticker(message.chat.id, stickers.SOMETHING_WRONG, message.message_id)

        error_msg = f"{emoji.ERROR} Exception:\n<code>{str(exception)}</code>\n\n<code>{message}</code>"
        for admin in constants.ADMINS:
            for chunk in utils.chunks(error_msg, 3000):
                self.bot.send_message(admin, utils.escape(chunk), parse_mode='HTML')

    # Handle text messages
    def _handle_text_messages(self, message: Message):
        if not message or not message.text:
            return

        if message.text.startswith('/'):
            at_mention = utils.get_atmention(message)
            if at_mention and at_mention != self.me.username:
                return

            cmd = utils.get_command(message)
            for action in self.actions:
                if cmd in action.get_cmds():
                    self._call_action(action, message)
                    return

        if not utils.is_for_me(message, self.me):
            return

        selected_actions = []
        for action in self.actions:
            for keyword in action.get_keywords():
                if keyword in message.text.lower():
                    selected_actions.append(action)

        if len(selected_actions) == 1:
            action = selected_actions[0]
            self._call_action(action, message)
        elif len(selected_actions) > 1:
            self.bot.reply_to(message,
                              emoji.ERROR + " Я не поняла, что ты имеешь в виду, пожалуйста выбери что-то одно:",
                              reply_markup=InlineKeyboardMarkup([[
                                  InlineKeyboardButton(action.get_name(),
                                                       callback_data=f"select_action:{action.__class__.__name__}")
                                  for action in selected_actions
                              ]]))
        elif message.text and not message.text.startswith('/'):
            action = next(filter(lambda a: a.__class__.__name__ == 'Reply', self.actions))
            self._call_action(action, message)

    # handle callbacks
    def _handle_callback_queries(self, call: CallbackQuery):
        if not call.data:
            return
        if call.data.startswith('select_action:'):
            cls = call.data.split(':')[1]
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            if call.message.reply_to_message:
                for action in self.actions:
                    if action.__class__.__name__ == cls:
                        action.call(call.message.reply_to_message)
                        return
        elif call.data.startswith('dice:'):
            for action in self.actions:
                if action.__class__.__name__ == 'Dice':
                    action.btn_pressed(call.message, call.data)

    def _call_action(self, action, message):
        try:
            action.call(message)
        except Exception as e:
            self._handle_errors(message, e)
