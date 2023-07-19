from typing import List

from language import abbrev_set, romannumeral_set, punct_set, intstr_to_text, symbol_set, roman_to_text
from token_types import CharClass, TokenGroup, TokenGroupClass


def tokenize(txt: str) -> List[str]:
    ret = []
    tok = ''
    oc = CharClass.NONE
    for c in txt:
        if c.isspace():
            nc = CharClass.WHITESPACE
        elif c.isalpha():
            nc = CharClass.LETTER
        elif c.isdigit():
            nc = CharClass.DIGIT
        else:
            nc = CharClass.SYMBOL

        if oc == nc:
            tok += c
        else:
            if tok:
                ret.append(tok)
            oc = nc
            tok = c
    ret.append(tok)
    return ret


def group_classify(toks: List[str]) -> List[TokenGroup]:
    ret = []
    while len(toks) > 0:
        tok = toks.pop(0)
        if tok[0].isspace():
            tg = TokenGroup([tok], TokenGroupClass.WHITESPACE)
            ret.append(tg)
        elif tok[0].isdigit():
            if len(toks) >= 2 and toks[0] == '.' and toks[1][0].isdigit():
                tg = TokenGroup([tok, toks.pop(0), toks.pop(0)], TokenGroupClass.TIME)
            elif len(ret) > 2 and ret[-3].tokens[0] == 'godz':
                g = [tok]
                if toks[0][0] == '.':
                    g.append(toks.pop(0))
                tg = TokenGroup(g, TokenGroupClass.TIME)
            else:
                g = [tok]
                while len(toks) > 1 and toks[0][0].isdigit():
                    g.append(toks.pop())
                tg = TokenGroup(g, TokenGroupClass.NUMBER)
            ret.append(tg)
        elif tok[0].isalpha():
            if tok in abbrev_set:
                g = [tok]
                if len(toks) > 0 and toks[0] == '.':
                    g.append(toks.pop(0))
                if tok == 'w' and len(g) < 2:
                    tg = TokenGroup(g, TokenGroupClass.WORD)
                else:
                    tg = TokenGroup(g, TokenGroupClass.ABBREV)
            else:
                roman = True
                for c in tok:
                    if c not in romannumeral_set:
                        roman = False
                        break
                if roman:
                    tg = TokenGroup([tok], TokenGroupClass.ROMAN)
                else:
                    tg = TokenGroup([tok], TokenGroupClass.WORD)
            ret.append(tg)
        else:
            if tok[0] in punct_set:
                tg = TokenGroup([tok], TokenGroupClass.PUNCTUATION)
                ret.append(tg)
            else:
                tg = TokenGroup([tok], TokenGroupClass.SYMBOL)
                ret.append(tg)
    return ret


def verbalize(groups: List[TokenGroup]):
    for grp in groups:
        if grp.tokenclass == TokenGroupClass.WORD:
            grp.verbalized.append(grp.tokens[0].lower())
        elif grp.tokenclass == TokenGroupClass.ABBREV:
            a = abbrev_set[grp.tokens[0]]
            if isinstance(a, str):
                grp.verbalized.append(a)
            else:
                grp.verbalized.extend(a)
        elif grp.tokenclass == TokenGroupClass.SYMBOL:
            s = grp.tokens[0][0]
            if s in symbol_set:
                s = symbol_set[s]
                if isinstance(s, str):
                    grp.verbalized.append(s)
                else:
                    grp.verbalized.extend(s)
        elif grp.tokenclass == TokenGroupClass.NUMBER:
            grp.verbalized.extend(intstr_to_text(grp.tokens[0]))
        elif grp.tokenclass == TokenGroupClass.ROMAN:
            grp.verbalized.extend(roman_to_text(grp.tokens[0]))
        elif grp.tokenclass == TokenGroupClass.TIME:
            grp.verbalized.extend(intstr_to_text(grp.tokens[0]))
            if len(grp.tokens) > 2:
                grp.verbalized.extend(intstr_to_text(grp.tokens[2]))
