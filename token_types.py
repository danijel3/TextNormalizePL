from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CharClass(Enum):
    NONE = 0,
    WHITESPACE = 1
    LETTER = 2,
    DIGIT = 3,
    SYMBOL = 4


class TokenGroupClass(Enum):
    UNKNOWN = 0,
    WHITESPACE = 1,
    WORD = 2,
    NUMBER = 3,
    ABBREV = 4,
    PUNCTUATION = 5,
    SYMBOL = 6,
    TIME = 7,
    ROMAN = 8


def grp_cls2str(cls: TokenGroupClass) -> str:
    return {TokenGroupClass.UNKNOWN: 'U',
            TokenGroupClass.WHITESPACE: '_',
            TokenGroupClass.WORD: 'W',
            TokenGroupClass.NUMBER: 'N',
            TokenGroupClass.ABBREV: 'A',
            TokenGroupClass.PUNCTUATION: 'P',
            TokenGroupClass.SYMBOL: 'S',
            TokenGroupClass.TIME: 'T',
            TokenGroupClass.ROMAN: 'R'
            }[cls]


@dataclass
class TokenGroup:
    tokens: List[str]
    tokenclass: TokenGroupClass
    verbalized: List[str] = field(default_factory=lambda: [])

    def tok2str(self):
        return ''.join(self.tokens)

    def tok2str_dbg(self):
        return '/'.join(self.tokens) + f'[{grp_cls2str(self.tokenclass)}]'

    def verb2str(self):
        return ' '.join(self.verbalized)


def grp_tok2str(groups: List[TokenGroup]) -> str:
    return ''.join([g.tok2str() for g in groups])


def grp_tok2str_dbg(groups: List[TokenGroup]) -> str:
    return '|'.join([g.tok2str_dbg() for g in groups])


def grp_verb2str(groups: List[TokenGroup]) -> str:
    return ' '.join(filter(lambda x: x, [g.verb2str() for g in groups]))
