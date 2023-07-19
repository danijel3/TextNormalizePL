import re
from typing import Tuple

import pl_core_news_lg

from language import number_to_text, roman_to_text, symbol_set, abbrev_set, parse_time, abbrev_period_set

nlp = pl_core_news_lg.load()


def is_roman_numeral(text: str) -> bool:
    for c in text:
        if c not in {'I', 'V', 'X', 'L', 'C', 'D', 'M'}:
            return False
    return True


ROMAN_NUM = nlp.vocab.add_flag(is_roman_numeral)

cleanup = re.compile(r'["/]')
nonascii = re.compile(r'[^\x00-\x7F\w]')
nonspeech = re.compile(r'\[\[.*?]]')

punct_to_keep = {',', '.', '?', '!', ':', ';'}


def pad(text: str, pad: str, len: int) -> str:
    ret = [text]
    for i in range(len - 1):
        ret.append(pad)
    return ret


def replunk(match: re.Match) -> str:
    return '_' * len(match.group())


def normalize(line: str, pad_token: str = '_') -> Tuple[str, str]:
    text = line.strip()
    text = nonspeech.sub(replunk, text)
    text = cleanup.sub('_', text)
    text = nonascii.sub('_', text)
    text = nlp(text)
    line = []
    orig = []
    for w in text:

        if w.text == '_':
            continue

        orig_text = w.text
        if w.is_punct:
            if w.text in symbol_set:
                n = symbol_set[w.text]
                line.extend(n)
                orig.extend(pad(orig_text, pad_token, len(n)))

            if w.text in punct_to_keep and orig:
                orig[-1] += w.text

            continue

        if w.morph.get('Abbr') or w.text in abbrev_period_set:
            lemma = w.lemma_

            if w.text in abbrev_period_set:
                lemma = ' '.join(abbrev_period_set[w.text])

            no_period = (lemma[0] == w.orth_[0] and lemma[-1] == w.orth_[-1])

            next_word = None
            try:
                next_word = next(w.rights).orth_
            except StopIteration:
                pass
            if next_word == '.' or no_period:
                lemma = lemma.split()
                line.extend(lemma)
                orig.extend(pad(orig_text, pad_token, len(lemma)))

                continue

        if w.text in abbrev_set:
            n = abbrev_set[w.text]
            line.extend(n)
            orig.extend(pad(orig_text, pad_token, len(n)))
            continue

        if w.like_num:
            n = number_to_text(w)
            if not n:
                continue
            line.extend(n)
            orig.extend(pad(orig_text, pad_token, len(n)))
            continue

        if w.check_flag(ROMAN_NUM):
            n = roman_to_text(w.text)
            line.extend(n)
            orig.extend(pad(orig_text, pad_token, len(n)))
            continue

        t = parse_time(w.text)
        if t:
            line.extend(t)
            orig.extend(pad(orig_text, pad_token, len(t)))
            continue

        if w.text[-1] == '+':
            if w.text == '+':
                line.append('plus')
                orig.append(orig_text)
            else:
                n = [w.text[:-1].lower(), 'plus']
                line.extend(n)
                orig.extend(pad(orig_text, pad_token, len(n)))
            continue

        line.append(w.lower_)
        orig.append(orig_text)

    return ' '.join(line), ' '.join(orig)


# unit test
if __name__ == '__main__':
    text = '[[oklaski]] Szanowni Państwo! W dniu 8 listopada zmarł Stefan Strzałkowski, nauczyciel, samorządowiec, burmistrz Białogardu, poseł na Sejm VI, VII i VIII kadencji.'
    # text = 'Kiedy, demokracja ma się lepiej? Kiedy demokracja w lepszy sposób znajduje odzwierciedlenie w tej Izbie, w izbach sejmikowych? Kiedy jest minimalny, rekordowy w ciągu 30 lat odsetek głosów nieważnych i jednocześnie rekordowa liczba głosów ważnych,bo wyższa nawet niż w 1989 r. - nie procentowo, ale w liczbach bezwzględnych. Te 18,5 mln świadczy o tym, że demokracja ma się tak dobrze, mogę powiedzieć, jak nigdy wcześniej. Bo czymże właśnie jest demokracja, jak nie prawem i jednocześnie wiar'
    # text = '(Początek posiedzenia o godz. 12 min 04)'

    n, o = normalize(text)

    print(n)
    print(o)
    #
    # assert (len(n.split()) == len(o.split()))
    #
    # for a, b in zip(n.split(), o.split()):
    #     print(a, b)
