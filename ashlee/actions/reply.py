from typing import List
from threading import Timer
from time import time

import openai
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
        start_time = time()
        if message.text.startswith('/'):
            if message.reply_to_message:
                text = message.reply_to_message.text
            else:
                text = utils.get_keyword(message)
        else:
            text = message.text
        prompt = "I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer.\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\nQ: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: I have no idea.\n\nQ: " + text + "\nA: "
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=1,
          max_tokens=1000,
        )
        sentence = response['choices'][0]['text']
        # sentence = None
        # if text:
        #     sl = len(text) // 200
        #     if sl < 2:
        #         sl = 2
        #     elif sl > 20:
        #         sl = 20
        #     sentence = pepe.generate_sentence_by_text(self.tgb.redis, text, sentences_limit=sl)
        # if not sentence:
        #     sentence = pepe.generate_sentence(self.tgb.redis)[0]
        # sentence = pepe.capitalise(sentence)
        consumed_time = time() - start_time
        dt = 1.0 - consumed_time
        if dt >= 0:
            Timer(dt, lambda: self.bot.reply_to(message, sentence)).start()
        else:
            self.bot.reply_to(message, sentence)
