from typing import List
from threading import Timer
from time import time

import openai
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action

history = {}


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
        prompt = "I am Ashley, a highly intelligent bot-girl with soul." \
                 "You can ask me anything!\n\nQ: Что такое #уясосало?\nA: Это бан!\n\nQ: Who was president of the " \
                 "United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\n" \
                 "Q: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: How does a " \
                 "telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear " \
                 "closer.\n\nQ: How many squigs are in a bonk?\nA: I have no idea what it is."
        if message.chat.id not in history:
            history[message.chat.id] = []
        for q, a in history[message.chat.id][-5::]:
            prompt += "\n\nQ: " + q + "\nA: " + a
        prompt += "\n\nQ: " + text + "\nA: "
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=1,
                max_tokens=500,
            )
            sentence = response['choices'][0]['text']
            history[message.chat.id].append((text, sentence))
        except openai.error.InvalidRequestError as e:
            sentence = "Произошла ошибка: " + str(e)

        consumed_time = time() - start_time
        dt = 1.0 - consumed_time
        if dt >= 0:
            Timer(dt, lambda: self.bot.reply_to(message, sentence)).start()
        else:
            self.bot.reply_to(message, sentence)
