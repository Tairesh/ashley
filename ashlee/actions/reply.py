from typing import List

from telebot.types import Message

from ashlee import emoji, utils, pepe
from ashlee.action import Action


class Reply(Action):

    def get_description(self) -> str:
        return 'сгенерировать немного бреда'

    def get_name(self) -> str:
        return emoji.DICE + ' Бред'

    def get_cmds(self) -> List[str]:
        return ['reply']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith('/'):
            if message.reply_to_message:
                text = message.reply_to_message.text
            else:
                text = utils.get_keyword(message)
        else:
            text = message.text

        sentence = None
        if text:
            sl = len(text) // 200
            if sl < 2:
                sl = 2
            elif sl > 20:
                sl = 20
            sentence = pepe.generate_sentence_by_text(self.tgb.redis, text, sentences_limit=sl)
        if not sentence:
            sentence = pepe.generate_sentence(self.tgb.redis)[0]

        self.bot.reply_to(message, pepe.capitalise(sentence))
