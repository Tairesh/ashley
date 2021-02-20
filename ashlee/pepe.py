import re
import random
import traceback
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing


r_alphabet = re.compile(r'[\w\d\-%#@^*_`]+|[.,:;?!><&/\\+=]+')

END_MARK = ('.', '!', '?', '\n', 'end')
NOSPACE_MARK = ('.', '!', '?', ':', ',', ';', '...', '..', ';', '!?', '???', '??', '?!', 'end', '\n')
CAPITALIZED = {'эшли', 'єшли', 'ешлі', 'єшлі',
               'илья', 'илье', 'илью', 'ильёй',
               'прохор', 'прохору', 'прохора', 'прохором'}


def gen_tokens(text):
    for token in r_alphabet.findall(text.lower()):
        yield token


def gen_bigrams(tokens):
    t0 = '$'
    for t1 in tokens:
        if t0 == '$' and t1 in {'эшли', 'єшли', 'ешлі', 'єшлі', 'эш', 'ashley', '.', ',', '!', ':', ';', '?'}:
            continue
        yield t0, t1
        if t1 in END_MARK:
            yield t1, '$'
            t0 = '$'
        else:
            t0 = t1


def gen_trigrams(tokens):
    t0, t1 = '$', '$'
    for t2 in tokens:
        yield t0, t1, t2
        if t2 in END_MARK:
            yield t1, t2, '$'
            yield t2, '$', '$'
            t0, t1 = '$', '$'
        else:
            t0, t1 = t1, t2


def key(a, b):
    return a + '->' + b


def train(db, text):
    for a, b, c in gen_trigrams(gen_tokens(text)):
        try:
            db.sadd(key(a, b), c)
        except Exception:
            pass


def remove_all_trigrams(db, text):
    trigrams = set(gen_trigrams(gen_tokens(text)))
    for a, b, c in trigrams:
        try:
            k = key(a, b)
            ar = [str(a.decode()) for a in db.smembers(k)]
            if c in ar:
                db.srem(k, c)
            if len(ar) <= 1:
                db.delete(k)
        except Exception:
            print(traceback.format_exc())
    return trigrams


def capitalise(phrase):
    resp = ""
    v = phrase.split()
    for x in v:
        if x in CAPITALIZED:
            resp += (" " + x.title())
        else:
            resp += (" " + x)

    return resp


def generate_sentence(db, start='', a='$', b='$') -> tuple:
    sentence = start
    tries = 0
    used_keys = [b]
    while tries < 100:
        ar = [str(a.decode()) for a in db.smembers(key(a, b))]
        if len(ar) == 0:
            break
        a, b = b, random.choice(ar)
        if b not in used_keys:
            used_keys.append(b)
        if b == '$' or b == 'end':
            break
        if b in NOSPACE_MARK or a == '$':
            sentence += b
        else:
            sentence += ' ' + b
        tries += 1
    if len(sentence) == 0:
        sentence = 'добро хуй сварился'
    return sentence, used_keys


def compile_sentences(db, sentences: list) -> str:
    if len(sentences) == 1:
        sentence = sentences[0]
    elif len(sentences) == 0:
        sentence, _ = generate_sentence(db)
    else:
        sentence = ''
        i = 0
        for s in sentences:
            if i < len(sentences)-1:
                test_char = s[-1::]
                if test_char == ' ':
                    test_char = s[-2:-1:]
                if test_char not in NOSPACE_MARK:
                    endmark = random.choice(('?', '!', '...', ',', ' —', '\n', ':')) + ' '
                else:
                    endmark = ' '
                s += endmark
            sentence += s
            i += 1
    return sentence


def generate_sentence_by_text(db, text: str, sentences_limit: int = 0) -> str:
    if not text:
        return generate_sentence(db)[0]

    sentences = []
    usedkeys = set()
    bigrams = list(gen_bigrams(gen_tokens(text)))

    if len(bigrams) > 1 and len(db.smembers(key(*bigrams[1]))):
        bigrams.pop(0)

    if len(bigrams):
        for t0, t1 in bigrams:
            if t1 == '$' or t0 in NOSPACE_MARK or t0 in usedkeys or t1 in usedkeys:
                continue
            if len(db.smembers(key(t0, t1))):
                a, b = t0, t1
                start = (a if a != '$' else '') + (' ' if b not in NOSPACE_MARK and a != '$' else '') + (
                    b if b != 'end' else '?')
                s, used = generate_sentence(db, start, a, b)
                sentences.append(s)
                usedkeys.add(a)
                usedkeys.add(b)
                for k in used:
                    if k not in usedkeys:
                        usedkeys.add(k)

    if len(sentences):
        random.shuffle(sentences)
        if sentences_limit and len(sentences) > sentences_limit:
            sentences = sentences[:sentences_limit]
        return compile_sentences(db, sentences) if len(sentences) > 1 else sentences[0]
    return generate_sentence(db)[0]

def split_to_lines(sentence: str) -> list:
    words = sentence.split(' ')
    lines = []
    current_line = []
    for word in words:
        if len(current_line) == 0 or len(' '.join(current_line)) + len(word) < 25:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if len(current_line):
        lines.append(' '.join(current_line))
    return lines


def _middle_color(img: Image) -> tuple:
    blob = img.make_blob(format='RGB')
    reds = []
    greens = []
    blues = []
    for cursor in range(img.width * img.height * 2, img.width * img.height, 3):
        reds.append(blob[cursor])
        greens.append(blob[cursor + 1])
        blues.append(blob[cursor + 2])
    red_middle = sum(reds) / (img.width * img.height)
    green_middle = sum(greens) / (img.width * img.height)
    blue_middle = sum(blues) / (img.width * img.height)
    return red_middle, green_middle, blue_middle


def memetize(file_name, sentence):
    with Image(filename=file_name) as img:
        black = False
        red_middle, green_middle, blue_middle = _middle_color(img)
        if red_middle > 200 or blue_middle > 200 or green_middle > 200:
            black = True

        with Drawing() as context:
            lines = split_to_lines(sentence)
            context.text_alignment = 'center'
            context.font = 'res/fonts/lobster.ttf'
            max_len = len(max(lines, key=lambda el: len(el)))
            size = 1.5 * img.width / max_len

            context.font_size = size
            metrics = context.get_font_metrics(img, sentence)

            x = int(img.width / 2)
            y = int(img.height - metrics.character_height/2)

            for line in reversed(lines):
                context.fill_color = Color('#000' if black else '#fff')
                context.stroke_color = Color('#fff' if black else '#000')
                context.stroke_width = 2
                context.text(x, y, line)
                y -= int(metrics.character_height)
                if y < 0:
                    break
            context(img)

            img.format = 'jpeg'
            img.save(filename=file_name)
