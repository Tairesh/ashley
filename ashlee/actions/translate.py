import json
import subprocess
import requests
from typing import List

from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Translate(Action):
    GOOGLE_LANGS = {'hmn', 'fr', 'sv', 'sq', 'am', 'la', 'de', 'ig', 'gu', 'fa', 'ar', 'ca', 'my', 'no', 'mr', 'da',
                    'en', 'eu', 'zh-CN', 'id', 'kk', 'pt', 'pa', 'mk', 'hi', 'ug', 'tl', 'ne', 'ny', 'te', 'zh-TW',
                    'ur', 'th', 'xh', 'mn', 'uk', 'yo', 'gl', 'ka', 'uz', 'fy', 'hu', 'ku', 'lt', 'pl', 'ro', 'st',
                    'ky', 'ta', 'cy', 'haw', 'tr', 'lo', 'be', 'fi', 'sr', 'az', 'or', 'tg', 'su', 'ps', 'zu', 'sk',
                    'sl', 'kn', 'si', 'km', 'hy', 'lv', 'eo', 'et', 'af', 'ja', 'lb', 'ceb', 'he', 'bs', 'rw', 'ht',
                    'sn', 'bg', 'mt', 'iw', 'hr', 'ml', 'mi', 'is', 'ha', 'ga', 'bn', 'el', 'nl', 'zh', 'mg', 'co',
                    'tt', 'ko', 'ms', 'ru', 'jw', 'it', 'yi', 'tk', 'cs', 'es', 'so', 'sw', 'vi', 'gd', 'sd', 'sm'}
    GOOGLE_TRANSLATE_API = "https://translation.googleapis.com/language/translate/v2"
    GOOGLE_CLOUD_KEY = None

    def get_description(self) -> str:
        return 'перевести текст'

    def get_name(self) -> str:
        return emoji.ABC + ' Translate'

    def get_cmds(self) -> List[str]:
        return ['trans', 't']

    def get_keywords(self) -> List[str]:
        return ['переведи']

    def after_loaded(self):
        self._authorize()

    def _authorize(self):
        google_cloud_key_command = "export GOOGLE_APPLICATION_CREDENTIALS=config/google-cloud-secret.json; " \
                                   "gcloud auth application-default print-access-token"
        self.GOOGLE_CLOUD_KEY = subprocess.Popen(google_cloud_key_command, shell=True,
                                                 stdout=subprocess.PIPE).stdout.read().decode().strip()

    def _translate(self, q, target_language, recursive=True) -> tuple:
        data = json.dumps({'q': q, 'target': target_language, 'format': 'text'}).encode('utf-8')
        try:
            req = requests.post(self.GOOGLE_TRANSLATE_API, data, headers={
                'Authorization': 'Bearer ' + self.GOOGLE_CLOUD_KEY,
                'Content-Type': 'application/json; charset=utf-8',
            })
            result = json.loads(req.content.decode('utf-8'))['data']['translations'][0]
            return result['detectedSourceLanguage'], result['translatedText']
        except requests.RequestException as e:
            if recursive:
                self._authorize()
                return self._translate(q, target_language, False)
            else:
                raise e

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        keyword = utils.get_keyword(message, False)
        words = keyword.split(' ')
        target_lang = 'en'
        if len(words) > 1 and words[0].lower() in self.GOOGLE_LANGS:
            target_lang = words[0].lower()
            text = ' '.join(words[1:])
        else:
            rm = message.reply_to_message
            if words[0].lower() in self.GOOGLE_LANGS and rm:
                target_lang = words[0].lower()
                text = rm.caption if rm.caption else rm.text
            else:
                text = keyword if not rm else (rm.caption if rm.caption else rm.text)

        if not text:
            example = f'Пример использования: <code>/{utils.get_command(message)} Text to translate</code>\n' \
                      'По-умолчанию я перевожу с любого языка на русский или с русского на английский. ' \
                      'Чтобы перевести на другой язык (например итальянский) укажите код языка: ' \
                      f'<code>/{utils.get_command(message)} IT Text to translate</code>'
            self.bot.reply_to(message, example, parse_mode='html')
            return

        detected_lang, translated_text = self._translate(text, target_lang)
        if detected_lang == target_lang:
            if detected_lang == 'en':
                target_lang = 'ru'
            else:
                target_lang = 'en'
            _, translated_text = self._translate(text, target_lang)
        self.bot.reply_to(message, f"<code>{translated_text}</code>", parse_mode='html')
