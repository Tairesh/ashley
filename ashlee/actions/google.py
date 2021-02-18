import googlesearch
from telegram import ParseMode, Update

from ashlee.action import Action
from ashlee import utils


class Google(Action):

    def get_regexes(self):
        return []

    def get_cmds(self):
        return ["google", "g"]

    @Action.save_data
    @Action.send_typing
    def get_action(self, update: Update, context):
        keyword = utils.get_keyword(update.message)

        if not keyword:
            update.message.reply_text(f"Usage example:\n`{utils.get_command(update.message)} how to kidnap a loli`",
                                      parse_mode=ParseMode.MARKDOWN)
            return

        try:
            url = next(googlesearch.search(keyword, stop=1))
            update.message.reply_text(text=url)
        except StopIteration:
            update.message.reply_sticker('CAADAgADxgADOtDfAeLvpRcG6I1bFgQ')
