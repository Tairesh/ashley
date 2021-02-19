import re

from ashlee import emoji, utils
from ashlee.action import Action


class Lemons(Action):

    def get_name(self) -> str:
        return emoji.LEMON + " Лимоны"

    @Action.save_data
    @Action.send_typing
    def call(self, message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message, False)
            args = keyword.split(' ') if keyword else []
        else:
            args = []
            search = re.search(r'(\d+)', message.text)
            if search:
                args.append(search.group(0))
        if len(args) > 0:
            try:
                count = int(args[0])
            except ValueError:
                self.tgb.bot.reply_to(message, "Непонятное число лимонов!")
                return
        else:
            count = 3

        if count > 3000:
            self.tgb.bot.reply_to(message, "Слишком много лимонов!")
            return
        if count < 1:
            self.tgb.bot.reply_to(message, "Слишком мало лимонов!")
            return

        self.tgb.bot.reply_to(message, text=emoji.LEMON * count)

    def get_keywords(self):
        return ["лимоны"]

    def get_cmds(self):
        return ["lemons"]
