from ashlee import emoji, utils
from ashlee.action import Action


class Lemons(Action):

    def get_description(self) -> str:
        return "проверить количество лимонов"

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        db_user = self.db.get_user(message.from_user.id)
        count = db_user.lemons
        if count == 0:
            self.bot.reply_to(message, "У тебя нет ни одного лимона!")
        else:
            self.bot.reply_to(message, f"Вот твои лимоны, "
                                       f"{utils.format_number(count, 'штук', 'штука', 'штуки')}: {emoji.LEMON * count}")

    def get_keywords(self):
        return ["лимоны"]

    def get_cmds(self):
        return ["lemons"]
