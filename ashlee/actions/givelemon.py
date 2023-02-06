from telebot.types import Message

from ashlee import emoji, utils, stickers, constants
from ashlee.action import Action


class Givelemon(Action):
    def get_description(self) -> str:
        return "передать лимон"

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    def get_keywords(self):
        return []

    def get_cmds(self):
        return ["give_lemon", "givelemon"]

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = utils.get_keyword(message, False)
        if not keyword:
            return self.bot.reply_to(
                message,
                f"Укажите ID лимона который хотите передать, например `/{utils.get_command(message)} 1`",
                parse_mode="Markdown",
            )
        keyword = keyword.split(" ")

        lemon_id = None
        for k in keyword:
            try:
                lemon_id = int(k)
                break
            except ValueError:
                continue

        if not lemon_id:
            return self.bot.send_sticker(
                message.chat.id, stickers.FOUND_NOTHING, message.message_id
            )

        lemon = self.db.get_lemon(lemon_id)
        if not lemon:
            return self.bot.send_sticker(
                message.chat.id, stickers.FOUND_NOTHING, message.message_id
            )

        if (
            lemon.owner_id != message.from_user.id
            and message.from_user.id not in constants.ADMINS
        ):
            return self.bot.send_sticker(
                message.chat.id, stickers.CANT_DO, message.message_id
            )

        recipient = None
        if message.reply_to_message:
            recipient = self.db.get_user(message.reply_to_message.from_user.id)

        for k in keyword:
            if k.startswith("@"):
                recipient = self.db.get_user_by_username(k[1:].lower())
                if recipient:
                    break
        if not recipient:
            self.bot.reply_to(
                message,
                "Нужно указать юзернейм получателя "
                "или отправить эту команду ответом на его сообщение!",
            )
            return

        self.db.update_lemon_owner(lemon_id, recipient.id)
        self.bot.reply_to(
            message,
            f"{emoji.LEMON} LMN #{lemon_id} успешно передан! "
            f"{utils.user_name(recipient, mention=True)}, проверяй!",
            parse_mode="Markdown",
        )
