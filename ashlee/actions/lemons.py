from os import getcwd
from os.path import join
from typing import Optional

from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Lemons(Action):
    DIR = join(getcwd(), 'res', 'lemons')

    def get_description(self) -> str:
        return "проверить количество лимонов"

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    def get_callback_start(self) -> Optional[str]:
        return "lemons:"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message, False)
            if keyword:
                keyword = int(keyword)
                lemon = self.db.get_lemon(keyword)
                if lemon is None:
                    self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
                    return
                self.bot.send_photo(
                    message.chat.id,
                    open(join(self.DIR, lemon.image), 'rb'),
                    f"{emoji.LEMON} LMN #{lemon.id}\n" + (
                        f"PWNED by {utils.user_name(self.db.get_user(lemon.owner_id), True, True, True)}"
                        if lemon.owner_id else "*Free*"
                    ),
                    message.message_id,
                    parse_mode='Markdown'
                )
                return

        lemons = [f"{emoji.LEMON} LMN #{lemon.id}" for lemon in self.db.get_user_lemons(message.from_user.id)]
        count = len(lemons)
        if count == 0:
            self.bot.reply_to(message, "У тебя нет ни одного лимона!")
        else:
            self.bot.reply_to(
                message,
                f"Вот твои лимоны, "
                f"{utils.format_number(count, 'штук', 'штука', 'штуки')}: {', '.join(lemons)}"
                f"\nПосмотреть лимоны по ID: `/lemon 1` покажет {emoji.LEMON} LMN #1",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"{emoji.LEMON} Посмотреть все", callback_data="lemons:view_all")
                ]], 1),
            )

    def btn_pressed(self, call: CallbackQuery):
        if call.data.endswith('view_all'):
            media = [InputMediaPhoto(open(join(self.DIR, lemon.image), 'rb'), f"LMN #{lemon.id}")
                     for lemon in self.db.get_user_lemons(call.from_user.id)]
            for chunk in utils.chunks(media, 10):
                self.bot.send_media_group(call.message.chat.id, chunk, reply_to_message_id=call.message.message_id)

    def get_keywords(self):
        return ["лимоны"]

    def get_cmds(self):
        return ["lemons", "lemon"]
