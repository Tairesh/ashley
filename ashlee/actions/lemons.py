from os import getcwd
from os.path import join

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Lemons(Action):
    DIR = join(getcwd(), 'res', 'lemons')

    def get_description(self) -> str:
        return "проверить количество лимонов"

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        keyword = utils.get_keyword(message, False)
        if keyword:
            keyword = int(keyword)
            lemon = self.db.get_nth_user_lemon(message.from_user.id, keyword - 1)
            if lemon is None:
                self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
                return
            self.bot.send_photo(
                message.chat.id,
                open(join(self.DIR, lemon.image), 'rb'),
                f"LMN #{lemon.id}\nPWNED by {utils.user_name(message.from_user, True, True)}",
                message.message_id
            )
            return

        db_user = self.db.get_user(message.from_user.id)
        count = db_user.lemons
        if count == 0:
            self.bot.reply_to(message, "У тебя нет ни одного лимона!")
        else:
            self.bot.reply_to(
                message,
                f"Вот твои лимоны, "
                f"{utils.format_number(count, 'штук', 'штука', 'штуки')}: {emoji.LEMON * count}"
                f"\nПосмотреть лимоны по порядковому номеру: `/lemon 1` покажет первый лимон",
                parse_mode='Markdown'
            )

    def get_keywords(self):
        return ["лимоны"]

    def get_cmds(self):
        return ["lemons", "lemon"]
