from ashlee import emoji
from ashlee.action import Action


class Lemons(Action):

    def get_regexes(self):
        return []

    def get_cmds(self):
        return ["lemons"]

    @Action.save_data
    @Action.send_typing
    def get_action(self, update, context):
        print(update, context)
        update.message.reply_text(
            text=emoji.LEMON * 3000)
