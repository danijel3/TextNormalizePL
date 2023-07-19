import re
from typing import List, Set, Optional

from spacy.tokens.token import Token

from token_types import TokenGroup, TokenGroupClass

punct_set = {'.', ',', '-', '!', '?', ':', '(', ')'}

# abbreviations requiring period after them
abbrev_period_set = {'art': ['atrykuł'], 'br': ['bieżącego', 'roku'],
                     'dr': ['doktor'], 'godz': ['godzina'], 'im': ['imienia'], 'in': ['innymi'], 'm': ['między'],
                     'np': ['na', 'przykład'], 'ok': ['około'], 'prof': ['profesor'], 'r': ['rok'],
                     'tj': ['to', 'jest'],
                     'tyg': ['tygodnia'], 'tys': ['tysięcy'], 'tzn': ['to', 'znaczy'], 'tzw': ['tak', 'zwany'],
                     'ub': ['ubiegłego'], 'ust': ['ustęp'], 'ww': ['wyżej', 'wymieniony'], 'św': ['święty'],
                     'w': ['wiek']}

abbrev_set = {'ARP': ['aerpe'], 'ASF': ['aesef'], 'AWS': ['awues'], 'BIG': ['beige'], 'CAF': ['ceaef'],
              'CBA': ['cebea'], 'CEIDG': ['ceidege'], 'CIT': ['cit'], 'COVID': ['kovid'], 'ELA': ['ela'],
              'EOG': ['eoge'], 'ETS': ['etees'], 'GUS': ['gus'], 'IPN': ['ipeen'], 'KGHM': ['kagehaem'], 'KIK': ['kik'],
              'KOWR': ['kaowuer'], 'KPO': ['kapeo'], 'KRUS': ['krus'], 'KUL': ['kul'], 'M': ['między'],
              'MSW': ['emeswu'], 'MSWiA': ['emeswuia'], 'NATO': ['nato'], 'NFOŚ': ['enfoś'], 'Np': ['na', 'przykład'],
              'OPZZ': ['opezetzet'], 'OUKiK': ['oukik'], 'Ok': ['około'], 'PAIH': ['paih'], 'PARP': ['parp'],
              'PCR': ['peceer'], 'PFR': ['peefer'], 'PFRON': ['pefron'], 'PGNiG': ['pegenig'], 'PIP': ['pip'],
              'PIT': ['pit'], 'PKB': ['pekabe'], 'PKP': ['pekape'], 'PL': ['peel'], 'PO': ['peo'], 'POLSA': ['polsa'],
              'POZ': ['poze'], 'PPS': ['pepees'], 'PR': ['peer'], 'PRL': ['peerel'], 'PSL': ['peesel'], 'PUP': ['pup'],
              'PiS': ['pis'], 'RDS': ['erdees'], 'REGON': ['regon'], 'RP': ['erpe'], 'SMS': ['esemes'],
              'TVP': ['tefaupe'], 'UE': ['ue'], 'UOKiK': ['uokik'], 'VAT': ['vat'], 'WE': ['wue'], 'WUP': ['wup'],
              'ZFA': ['zetefa'], 'ZFRON': ['zefron'], 'ZUS': ['zus'],
              'PR24': ['polskie', 'radio', 'dwadzieścia', 'cztery'], 'TVP3': ['tefaupe', 'trzy'], 'S&F': ['esenef']}

romannumeral_set = {'I', 'V', 'X', 'L', 'C', 'M'}

symbol_set = {'%': ['procent'], '+': ['plus'], '#': ['hasz', 'tag']}


def get_abbrev_candidates(lines: List[List[TokenGroup]]) -> Set[str]:
    ret = set()
    for grp in lines:
        for i in range(len(grp) - 3):
            cand = False
            if grp[i].tokenclass == TokenGroupClass.WORD:
                # detect all capital letters
                t = grp[i].tokens[0]
                for c in t[1:]:
                    if c.isupper():
                        cand = True
                        break
                if grp[i + 1].tokens[0] == '.':
                    # detect period followed by lower-case word
                    if grp[i + 2].tokenclass == TokenGroupClass.WORD and grp[i + 2].tokens[0].islower():
                        cand = True
                    # detect period followed by number - has false positives
                    if grp[i + 3].tokenclass == TokenGroupClass.WORD and grp[i + 3].tokens[0].islower():
                        cand = True
                    # detect period followed by time (eg. godz)
                    if grp[i + 3].tokenclass == TokenGroupClass.NUMBER or grp[i + 3].tokenclass == TokenGroupClass.TIME:
                        cand = True
            if cand:
                ret.add(grp[i].tokens[0])

    return ret


u1k = 'tysiąc'
u2_4k = 'tysiące'
u5_9k = 'tysięcy'
u1m = 'milion'
u2_4m = 'miliony'
u5_9m = 'milionów'
h1_9 = {1: 'sto', 2: 'dwieście', 3: 'trzysta', 4: 'czterysta', 5: 'pięćset', 6: 'sześćset', 7: 'siedemset',
        8: 'osiemset', 9: 'dziewięćset'}
t2_9 = {2: 'dwadzieścia', 3: 'trzydzieści', 4: 'czterdzieści', 5: 'pięćdziesiąt', 6: 'sześćdziesiąt',
        7: 'siedemdziesiąt', 8: 'osiemdziesiąt', 9: 'dziwiędziesiąt'}
d0_19 = {0: 'zero', 1: 'jeden', 2: 'dwa', 3: 'trzy', 4: 'cztery', 5: 'pięć', 6: 'sześć', 7: 'siedem', 8: 'osiem',
         9: 'dziewięć', 10: 'dziesięć', 11: 'jedenaście', 12: 'dwanaście', 13: 'trzynaście', 14: 'czternaście',
         15: 'piętnaście', 16: 'szesnaście', 17: 'siedemnaście', 18: 'osiemnaście', 19: 'dziewiętnaście'}

dig_cleanup = re.compile(r'\D')


def int_to_str(num: int) -> List[str]:
    ret = []
    if num == 0:
        return [d0_19[num]]
    if num > 999:
        t = num // 1000
        num = num % 1000
        if t >= 1000:
            m = t // 1000
            t = t % 1000
            if m % 10 == 1:
                if m > 1:
                    ret.extend(int_to_str(m))
                ret.append(u1m)
            elif 2 <= m % 10 <= 4:
                ret.extend(int_to_str(m))
                ret.append(u2_4m)
            else:
                ret.extend(int_to_str(m))
                ret.append(u5_9m)
            if t == 0:
                return ret
        if t % 10 == 1:
            if t > 1:
                ret.extend(int_to_str(t))
            ret.append(u1k)
        elif 2 <= t % 10 <= 4:
            ret.extend(int_to_str(t))
            ret.append(u2_4k)
        else:
            ret.extend(int_to_str(t))
            ret.append(u5_9k)
        if num == 0:
            return ret
    if num > 99:
        t = num // 100
        num = num % 100
        ret.append(h1_9[t])
    if num > 19:
        t = num // 10
        num = num % 10
        ret.append(t2_9[t])
    if num > 0:
        ret.append(d0_19[num])
    return ret


def intstr_to_text(dig: str) -> Optional[List[str]]:
    dig = dig_cleanup.sub('', dig)
    if not dig:
        return None
    return int_to_str(int(dig))


roman_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}


def roman_to_text(num: str) -> List[str]:
    val = 0
    i = 0
    while i < len(num):
        x = roman_val[num[i]]
        if i + 1 < len(num):
            xn = roman_val[num[i + 1]]
            if x >= xn:
                val += x
                i += 1
            else:
                val += xn - x
                i += 2
        else:
            val += x
            i += 1
    return intstr_to_text(str(val))


def number_to_text(num: Token) -> Optional[List[str]]:
    form = num.morph.get('NumForm')
    if form and form[0] == 'Word':
        return [num.lower_]
    if num.is_digit:
        return intstr_to_text(num.text)
    else:
        if not num.is_alpha:
            if ',' in num.text:
                tok = num.text.split(',')
                if len(tok) == 2:
                    ret = intstr_to_text(tok[0])
                    ret.append('przecinek')
                    ret.extend(intstr_to_text(tok[1]))
                    return ret
            if '/' in num.text:
                tok = num.text.split('/')
                if len(tok) == 2:
                    ret = intstr_to_text(tok[0])
                    ret.append('przez')
                    ret.extend(intstr_to_text(tok[1]))
                    return ret
        return [num.lower_]


def parse_time(time: str) -> Optional[List[str]]:
    if 4 <= len(time) <= 5 and ':' in time and time[0].isdigit() and time[3].isdigit():
        ret = []
        if len(time) == 4 and time[1] == ':' and time[2].isdigit():
            ret.extend(intstr_to_text(time[0:1]))
            ret.extend(intstr_to_text(time[2:4]))
            return ret
        elif len(time) == 5 and time[2] == ':' and time[1].isdigit() and time[4].isdigit():
            ret.extend(intstr_to_text(time[0:2]))
            ret.extend(intstr_to_text(time[3:5]))
            return ret
    else:
        return None
