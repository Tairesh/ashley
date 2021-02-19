import importlib
import logging
import os
import threading

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji, constants, utils


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class TelegramBot:

    def __init__(self, token, api_keys, db, clean=False):
        self.token = token
        self.api_keys = api_keys
        self.db = db
        self.clean = clean
        self.actions = []

        self.bot = TeleBot(token, skip_pending=clean)
        self.me = self.bot.get_me()

        # Load classes in folder 'actions'
        self._load_actions()

        self.bot.add_message_handler({'function': self._handle_text_messages, 'filters': {
            'func': lambda m: m.text and not m.forward_from_chat,
            'content_types': ['text'],
        }})

    # Start the bot
    def bot_start_polling(self):
        for admin in constants.ADMINS:
            self.bot.send_message(admin, emoji.INFO + ' I was restarted')

    # Go in idle mode
    def bot_idle(self):
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
                action.remove_action()
                break

    def reload_plugin(self, module_name):
        self.remove_action(module_name)

        try:
            module_path = f"ashlee.actions.{module_name}"
            module = importlib.import_module(module_path)

            importlib.reload(module)

            action_class = getattr(module, module_name.capitalize())
            action_class(self)
        except Exception as ex:
            msg = f"Plugin '{module_name.capitalize()}' can't be reloaded: {ex}"
            logging.warning(msg)
            raise ex

    # Handle all telegram and telegram.ext related errors
    def _handle_tg_errors(self, message, exception):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{exception} - {cls_name} - {message}")

        if not message:
            return

        error_msg = f"{emoji.ERROR} Telegram ERROR: *{exception}*"

        if message:
            self.bot.reply_to(message, text=error_msg, parse_mode='Markdown')

        for admin in constants.ADMINS:
            self.bot.send_message(admin, error_msg + f'\n```{message}```', parse_mode='Markdown')

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
            self.bot.reply_to(message, "idk idc")

    def _call_action(self, action, message):
        try:
            action.call(message)
        except ApiException as e:
            self._handle_tg_errors(message, e)
