import importlib
import logging
import os
import threading

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.error import InvalidToken
from ashlee import emoji, constants


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class TelegramBot:

    def __init__(self, token, db, clean=False):
        self.token = token
        self.db = db
        self.clean = clean
        self.actions = []

        try:
            self.updater = Updater(token)
        except InvalidToken as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Bot token not valid")

        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        # Load classes in folder 'actions'
        self._load_actions()

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self._handle_tg_errors)

    # Start the bot
    def bot_start_polling(self):
        self.updater.start_polling(clean=self.clean)

        for admin in constants.ADMINS:
            self.updater.bot.send_message(admin, emoji.INFO + ' I was restarted')

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def _load_actions(self):
        threads = list()

        for _, _, files in os.walk(os.path.join(constants.SRC_DIR, constants.ACTIONS_DIR)):
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
            module_path = f"{constants.SRC_DIR}.{constants.ACTIONS_DIR}.{module_name}"
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
            module_path = f"{constants.SRC_DIR}.{constants.ACTIONS_DIR}.{module_name}"
            module = importlib.import_module(module_path)

            importlib.reload(module)

            plugin_class = getattr(module, module_name.capitalize())
            plugin_class(self)
        except Exception as ex:
            msg = f"Plugin '{module_name.capitalize()}' can't be reloaded: {ex}"
            logging.warning(msg)
            raise ex

    # Handle all telegram and telegram.ext related errors
    def _handle_tg_errors(self, update, error):
        print(update, error)
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{error} - {cls_name} - {update}")

        if not update:
            return

        error_msg = f"{emoji.ERROR} Telegram ERROR: *{error.error}*"

        if update.message:
            update.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)
        elif update.callback_query:
            update.callback_query.message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN)

        for admin in constants.ADMINS:
            self.updater.bot.send_message(admin, error_msg + f'\n<code>{update}</code>', parse_mode='HTML')
