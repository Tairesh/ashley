from ashlee import emoji, utils, constants
from ashlee.action import Action


class Givelemons(Action):

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.LEMON + " Дать лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        keyword = utils.get_keyword(message, False)
        if not keyword:
            self.bot.reply_to(message, "Нужно указать количество лимонов!")
            return
        keyword = keyword.split(' ')

        recipient = None
        if message.reply_to_message:
            recipient = self.db.get_user(message.reply_to_message.user.id)
        else:
            for k in keyword:
                if k.startswith('@'):
                    recipient = self.db.get_user_by_username(k[1:].lower())
                    if recipient:
                        break
        if not recipient:
            self.bot.reply_to(message, "Нужно указать юзернейм получателя "
                                       "или отправить эту команду ответом на его сообщение!")
            return

        count = 0
        for k in keyword:
            try:
                count = int(k)
                break
            except ValueError:
                continue
        if count <= 0:
            self.bot.reply_to(message, "Нужно указать положительное число лимонов!")
            return

        sender = self.db.get_user(message.from_user.id)
        if count > sender.lemons and sender.id not in constants.ADMINS:
            self.bot.reply_to(message, f"У вас {sender.lemons} {emoji.LEMON} "
                                       f"а этого недостаточно чтобы передать {count} {emoji.LEMON}")
            return

        print(f"передаём {recipient.id} {count} {recipient.lemons + count}")
        self.db.update_user_lemons(recipient.id, recipient.lemons + count)
        self.bot.reply_to(message, f"Вы передали {count} {emoji.LEMON}, "
                                   f"{utils.user_name(recipient, True, True)}, проверяй!")

    def get_keywords(self):
        return []

    def get_cmds(self):
        return ["givelemons", "give_lemons"]
