import importlib
import logging
import os
import threading
import traceback
from typing import Dict, List, Tuple

from redis import StrictRedis
from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import (
    Message,
    User,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    BotCommand,
)

from ashlee import emoji, constants, utils, stickers, pepe
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
        self.welcomes: List[Tuple[threading.Timer, int, int, int]] = []

        self.bot: TeleBot = TeleBot(token, skip_pending=clean)
        self.me: User = self.bot.get_me()
        self.db.save_user_and_chat(self.me, None)

        # Load classes in folder 'actions'
        self._load_actions()

        self.bot.add_message_handler(
            {
                "function": self._handle_text_messages,
                "filters": {
                    "func": lambda m: m.text and not m.forward_from_chat,
                    "content_types": ["text"],
                },
                "pass_bot": False,
            }
        )

        self.bot.add_callback_query_handler(
            {
                "function": self._handle_callback_queries,
                "filters": {},
                "pass_bot": False,
            }
        )

        self.bot.add_message_handler(
            {
                "function": self._handle_new_members,
                "filters": {
                    "content_types": ["new_chat_members"],
                },
                "pass_bot": False,
            }
        )
        self.bot.add_message_handler(
            {
                "function": self._process_welcomes,
                "filters": {
                    "content_types": [
                        "animation",
                        "audio",
                        "contact",
                        "dice",
                        "document",
                        "location",
                        "photo",
                        "poll",
                        "sticker",
                        "venue",
                        "video",
                        "video_note",
                        "voice",
                    ],
                },
                "pass_bot": False,
            }
        )

    # Start the bot
    def bot_start_polling(self):
        for admin in constants.ADMINS:
            self.bot.send_message(admin, emoji.INFO + " I was restarted")

    # Go in idle mode
    def bot_idle(self):
        if self.debug:
            self.bot.polling(True, True)
        else:
            self.bot.infinity_polling()

    def _load_actions(self):
        threads = []

        for _, _, files in os.walk(os.path.join("ashlee", "actions")):
            for file in files:
                if not file.lower().endswith(".py"):
                    continue
                if file.startswith("_") or file.startswith("."):
                    continue

                threads.append(self._load_action(file))

        # Make sure that all plugins are loaded
        for thread in threads:
            thread.join()

        commands = []
        for action in self.actions:
            if len(action.get_cmds()) == 0 or not action.get_description():
                continue
            commands.append(BotCommand(action.get_cmds()[0], action.get_description()))
        self.bot.set_my_commands(commands)

    # pylint: disable=W0703
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

    def reload_actions(self):
        for action in self.actions:
            action.after_unload()
        self.actions.clear()
        self._load_actions()

    # Handle all errors
    def _handle_errors(self, message, exception):
        cls_name = f"Class: {type(self).__name__}"
        logging.error(f"{exception} - {cls_name} - {message}")

        if message:
            self.bot.send_sticker(
                message.chat.id, stickers.SOMETHING_WRONG, message.message_id
            )

        error_msg = (
            f"{emoji.ERROR} Exception: <code>{exception.__class__.__name__}</code>\n"
            f"Request: <code>{utils.escape(message.text)}</code>\n"
            f"\n<code>{utils.escape((traceback.format_exc()))}</code>"
        )
        for admin in constants.ADMINS:
            for chunk in utils.chunks(error_msg, 3000):
                self.bot.send_message(admin, chunk, parse_mode="HTML")

    def _process_welcomes(self, message: Message):
        if message and message.from_user:
            for w in self.welcomes:
                timer, chat_id, message_id, member_id = w
                if chat_id == message.chat.id and member_id == message.from_user.id:
                    timer.cancel()
                    try:
                        self.bot.delete_message(chat_id, message_id)
                    except ApiException:
                        pass
                    self.welcomes.remove(w)

    # Handle text messages
    def _handle_text_messages(self, message: Message):
        self._process_welcomes(message)

        if not message or not message.text:
            return

        if message.text.startswith("/"):
            at_mention = utils.get_atmention(message)
            if at_mention and at_mention != self.me.username:
                return

            cmd = utils.get_command(message)
            settings = self.db.get_chat_settings(message.chat.id)
            for action in self.actions:
                if cmd in action.get_cmds() and (
                    action.is_not_flood() or not settings or settings.enabled_replies
                ):
                    action.call(message)
                    return

        if not utils.is_for_me(message, self.me):
            return

        selected_actions = []
        for action in self.actions:
            for keyword in action.get_keywords():
                if (
                    keyword in message.text.lower()
                    and len(message.text) <= len(keyword) + 10
                ):
                    selected_actions.append(action)
                    break

        if len(selected_actions) == 1:
            action = selected_actions[0]
            action.call(message)
        elif len(selected_actions) > 1:
            self.bot.reply_to(
                message,
                emoji.ERROR
                + " Я не поняла, что ты имеешь в виду, пожалуйста выбери что-то одно:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                action.get_name(),
                                callback_data=f"select_action:{action.__class__.__name__}",
                            )
                            for action in selected_actions
                        ]
                    ]
                ),
            )
        elif message.text and not message.text.startswith("/"):
            settings = self.db.get_chat_settings(message.chat.id)
            if not settings or settings.enabled_replies:
                reply_action = next(
                    filter(lambda a: a.__class__.__name__ == "Reply", self.actions)
                )
                reply_action.call(message)
            pepe.train(self.redis, message.text)

    # handle callbacks
    def _handle_callback_queries(self, call: CallbackQuery):
        if not call.data:
            return

        if (
            call.message.reply_to_message
            and call.message.reply_to_message.from_user.id != call.from_user.id
        ):
            return

        if call.data.startswith("select_action:"):
            cls = call.data.split(":")[1]
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            if call.message.reply_to_message:
                for action in self.actions:
                    if action.__class__.__name__ == cls:
                        action.call(call.message.reply_to_message)
                        return
        else:
            for action in self.actions:
                cs = action.get_callback_start()
                if cs and call.data.startswith(cs):
                    action.btn_pressed(call)

    def _handle_new_members(self, message: Message):
        if message.new_chat_members:
            for member in message.new_chat_members:
                if member.id == self.me.id:
                    reply_action = next(
                        filter(lambda a: a.__class__.__name__ == "Start", self.actions)
                    )
                    reply_action.call(message)
                    continue
                if message.from_user and message.from_user.id != member.id:
                    continue

                text = None
                user_name = utils.user_name(member, True, True, True, "HTML")
                if message.chat.id == -1001150487023:  # Cataclysm DDA
                    text = (
                        f"{user_name} ты зашёл в чат Cataclysm DDA, "
                        f"перед тобой {emoji.SOAP} <code>soap (10)</code> со стола и "
                        f"{emoji.BREAD} <code>flat bread (filthy)</code> с параши. "
                        f"Что выберешь? На размышление 120 секунд а затем бан."
                    )
                elif message.chat.id == -1001298015134:  # Peerojoque
                    text = (
                        f"{user_name} отправьте любое сообщение в течении 120 секунд "
                        f"чтобы не получить бан нахуй"
                    )
                elif message.chat.id == -1001395369125:  # old cdda
                    text = (
                        f"{user_name} отправьте любое сообщение в течении 120 секунд "
                        f"чтобы не получить бан нахуй"
                    )
                if text:
                    msg = self.bot.reply_to(message, text, parse_mode="HTML")

                    def ban_user():
                        try:
                            self.bot.delete_message(msg.chat.id, msg.message_id)
                        except ApiException:
                            pass
                        try:
                            self.bot.delete_message(message.chat.id, message.message_id)
                        except ApiException:
                            pass
                        self.bot.kick_chat_member(msg.chat.id, member.id)

                    t = threading.Timer(120.0, ban_user)
                    t.start()
                    self.welcomes.append((t, msg.chat.id, msg.message_id, member.id))
