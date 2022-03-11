import random
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Chotamuhohlov(Action):

    WHOS = ('Министерства Обороны РФ', 'МИД РФ', 'Сергея Лаврова', 'Маргариты Симоньян',
            'Владимира Путина', 'Дмитрия Пескова', 'Владимира Володина', 'Дмитрия Медведева',
            'Роскомнадзора', 'Министерства Правды РФ', 'российских СМИ')
    NEWS_WHO = ('наркоманы', 'фашисты', 'бендеровцы', 'бойцы Азова', 'предатели', 'американцы',
                'сепаратисты', 'сатанисты', 'провокаторы', 'мутанты')
    NEWS_ACTION = ('спонсировали', 'готовили', 'разрабатывали', 'создавали', 'производили',
                   'запускали', 'планировали', 'обучали')
    NEWS_WHOM = ('химическое оружие', 'тараканов-убийц', '"грязную" бомбу', 'коронавирус',
                 'биологическое оружие', 'генно-модифицированных половцев', 'боевые наркотики',
                 'детей-снайперов', 'агрессивных клонов Степана Бандеры', 'чупакабру')
    NEWS_WHERE = ('в секретных лабораториях под Харьковом', 'на Украине', 'под Киевом')

    def get_description(self) -> str:
        return 'чё там у хохлов?'

    def get_name(self) -> str:
        return emoji.QUESTION + ' Чё там у хохлов?'

    def get_cmds(self) -> List[str]:
        return ['cho_tam_u_hohlov']

    def get_keywords(self) -> List[str]:
        return ['чё там у хохлов', 'че там у хохлов']

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        text = f"По данным {random.choice(self.WHOS)}, {random.choice(self.NEWS_WHO)} {random.choice(self.NEWS_WHERE)}" \
               f" {random.choice(self.NEWS_ACTION)} {random.choice(self.NEWS_WHOM)}"
        self.bot.reply_to(message, text)
