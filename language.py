from typing import List, Set

from token_types import TokenGroup, TokenGroupClass

punct_set = {'.', ',', '-', '!', '?', ':', '(', ')'}

abbrev_set = {'ARP': 'aerpe', 'ASF': 'aesef', 'AWS': 'awues', 'BIG': 'beige', 'CAF': 'ceaef', 'CBA': 'cebea',
              'CEIDG': 'ceidege', 'CIT': 'cit', 'COVID': 'kovid', 'ELA': 'ela', 'EOG': 'eoge', 'ETS': 'etees',
              'GUS': 'gus', 'IPN': 'ipeen', 'KGHM': 'kagehaem', 'KIK': 'kik', 'KOWR': 'kaowuer', 'KPO': 'kapeo',
              'KRUS': 'krus', 'KUL': 'kul', 'M': 'między', 'MSW': 'emeswu', 'MSWiA': 'emeswuia', 'NATO': 'nato',
              'NFOŚ': 'enfoś', 'Np': ['na', 'przykład'], 'OPZZ': 'opezetzet', 'OUKiK': 'oukik', 'Ok': 'około',
              'PAIH': 'paih', 'PARP': 'parp', 'PCR': 'peceer', 'PFR': 'peefer', 'PFRON': 'pefron', 'PGNiG': 'pegenig',
              'PIP': 'pip', 'PIT': 'pit', 'PKB': 'pekabe', 'PKP': 'pekape', 'PL': 'peel', 'PO': 'peo', 'POLSA': 'polsa',
              'POZ': 'poze', 'PPS': 'pepees', 'PR': 'peer', 'PRL': 'peerel', 'PSL': 'peesel', 'PUP': 'pup',
              'PiS': 'pis', 'RDS': 'erdees', 'REGON': 'regon', 'RP': 'erpe', 'SMS': 'esemes', 'TVP': 'tefaupe',
              'UE': 'ue', 'UOKiK': 'uokik', 'VAT': 'vat', 'WE': 'wue', 'WUP': 'wup', 'ZFA': 'zetefa', 'ZFRON': 'zefron',
              'ZUS': 'zus', 'art': 'atrykuł', 'br': ['bieżącego', 'roku'], 'dr': 'doktor', 'godz': 'godzina',
              'im': 'imienia', 'in': 'innymi', 'm': 'między', 'np': ['na', 'przykład'], 'ok': 'około',
              'prof': 'profesor', 'r': 'rok', 'tj': ['to', 'jest'], 'tyg': 'tygodnia', 'tys': 'tysięcy',
              'tzn': ['to', 'znaczy'], 'tzw': ['tak', 'zwany'], 'ub': 'ubiegłego', 'ust': 'ustęp',
              'ww': ['wyżej', 'wymieniony'], 'św': 'święty', 'w': 'wiek'}
romannumeral_set = {'I', 'V', 'X', 'L', 'C', 'M'}

symbol_set = {'%': 'procent', '+': 'plus', '#': ['hasz', 'tag']}


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


d1_10 = {1: 'jeden', 2: 'dwa', 3: 'trzy', 4: 'cztery', 5: 'pięć', 6: 'sześć', 7: 'siedem', 8: 'osiem', 9: 'dziewięć'}
u1k = 'tysiąc'
u2_4k = 'tysiące'
u5_9k = 'tysięcy'
h1_9 = {1: 'sto', 2: 'dwieście', 3: 'trzysta', 4: 'czterysta', 5: 'pięćset', 6: 'sześćset', 7: 'siedemset',
        8: 'osiemset', 9: 'dziewięćset'}
t2_9 = {2: 'dwadzieścia', 3: 'trzydzieści', 4: 'czterdzieści', 5: 'pięćdziesiąt', 6: 'sześćdziesiąt',
        7: 'siedemdziesiąt', 8: 'osiemdziesiąt', 9: 'dziwiędziesiąt'}
digits = {0: 'zero', 1: 'jeden', 2: 'dwa', 3: 'trzy', 4: 'cztery', 5: 'pięć', 6: 'sześć', 7: 'siedem', 8: 'osiem',
          9: 'dziewięć', 10: 'dziesięć', 11: 'jedenaście', 12: 'dwanaście', 13: 'trzynaście', 14: 'czternaście',
          15: 'piętnaście', 16: 'szesnaście', 17: 'siedemnaście', 18: 'osiemnaście', 19: 'dziewiętnaście'}


def integer_to_text(dig: str) -> List[str]:
    ret = []
    num = int(dig)
    if num == 0:
        return [digits[num]]
    if num > 999:
        d = num // 1000
        num = num % 1000
        if d == 1:
            ret.append(u1k)
        elif 2 <= d <= 4:
            ret.append(d1_10[d])
            ret.append(u2_4k)
        elif 5 <= d <= 9:
            ret.append(d1_10[d])
            ret.append(u5_9k)
    if num > 99:
        d = num // 100
        num = num % 100
        ret.append(h1_9[d])
    if num > 19:
        d = num // 10
        num = num % 10
        ret.append(t2_9[d])
    if num > 0:
        ret.append(digits[num])
    return ret


roman_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9',
             'X': '10', 'XX': '20', 'XIX': '19', 'C': '100'}


def roman_to_text(num: str) -> List[str]:
    if num in roman_map:
        return integer_to_text(roman_map[num])

    # DEBUG
    # print('ROM: ' + num)
    return ['??']
