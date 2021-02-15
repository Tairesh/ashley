import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.error import InvalidToken
from ashlee import emoji, constants


class TelegramBot:

    def __init__(self, token, clean=False):
        self.token = token
        self.clean = clean

        try:
            self.updater = Updater(token)
        except InvalidToken as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Bot token not valid")

        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        # Handle all Telegram related errors
        self.dispatcher.add_error_handler(self._handle_tg_errors)

        self.dispatcher.add_handler(CommandHandler('test', self._test_command))

    # Start the bot
    def bot_start_polling(self):
        self.updater.start_polling(clean=self.clean)

        for admin in constants.ADMINS:
            self.updater.bot.send_message(admin, emoji.INFO + ' I was restarted')

    # Go in idle mode
    def bot_idle(self):
        self.updater.idle()

    def _test_command(self, update, context):
        print(update, context)
        update.message.reply_text(text=emoji.LEMON * 5000)

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
