from ashlee import emoji, utils, constants
from ashlee.action import Action


class Takelemons(Action):

    def get_description(self):
        return None

    def get_name(self) -> str:
        return emoji.LEMON + " Забрать лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        if message.from_user.id not in constants.ADMINS:
            self.bot.reply_to(message, "Нельзя забирать лимоны у других! Заработай денег и купи их себе честно!")
            return

        keyword = utils.get_keyword(message, False)
        if not keyword:
            self.bot.reply_to(message, "Нужно указать количество лимонов!")
            return
        keyword = keyword.split(' ')

        donor = None
        if message.reply_to_message:
            donor = self.db.get_user(message.reply_to_message.from_user.id)

        for k in keyword:
            if k.startswith('@'):
                donor = self.db.get_user_by_username(k[1:].lower())
                if donor:
                    break
        if not donor:
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

        taker = self.db.get_user(message.from_user.id)
        if taker.id == donor.id:
            self.bot.reply_to(message, "Нет никакого, совершенно никакого смысла передавать лимоны самому себе. "
                                       "Их от этого не станет больше!")
            return

        self.db.update_user_lemons(donor.id, donor.lemons - count)
        self.db.update_user_lemons(taker.id, taker.lemons + count)
        self.bot.reply_to(message, f"Вы забрали {count} {emoji.LEMON}!\n"
                                   f"{utils.user_name(donor, True, True)}, проверяй!")

    def get_keywords(self):
        return []

    def get_cmds(self):
        return ["take_lemons", "takelemons", "takelemon", "take_lemon"]
