from ashlee import emoji, utils
from ashlee.action import Action


class Lemonstop(Action):

    def get_description(self) -> str:
        return "Топ участников чата по лимонам"

    def get_name(self) -> str:
        return emoji.LEMON + " Топ богачей"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        if message.chat.id == message.from_user.id:
            self.bot.reply_to(message, "В этом чате самый богатый — это ты!")
            return

        chat = self.db.get_chat(message.chat.id)
        users = self.db.get_users(chat.users)
        if len(users) == 0:
            self.bot.reply_to(message, f"{emoji.ERROR} В чате нет ни одного юзера! Это вообще как??")
            return

        users = sorted(filter(lambda u: u.lemons > 0, users), key=lambda u: u.lemons, reverse=True)
        if len(users) == 0:
            self.bot.reply_to(message, f"{emoji.SEARCH} В чате ни у кого нет лимонов, лол чё за чат нищебродов!")
            return
        users = users[:10]

        text = f"{emoji.INFO} <b>Топ богачей</b>:\n"
        for i, user in enumerate(users):
            text += f"{i+1}. {utils.user_name(user)} — {user.lemons} {emoji.LEMON}\n"
        self.bot.reply_to(message, text, parse_mode='HTML')

    def get_keywords(self):
        return ["топ по лимонам", "кто самый богатый"]

    def get_cmds(self):
        return ["lemonstop", "lemons_top", "toplemons", "top_lemons", "lemon_top", "lemontop"]
