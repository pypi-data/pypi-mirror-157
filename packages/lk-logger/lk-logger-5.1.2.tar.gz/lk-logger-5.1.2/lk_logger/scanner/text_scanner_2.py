"""
index based text scanner.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
import typing as t


class PairType:
    @dataclass
    class Plain:
        text: str
        symbol: tuple = ()
        children: list | tuple = ()
    
    @dataclass
    class Pair:
        text: str
        symbol: tuple[str, str]
        children: list | tuple


# noinspection PyArgumentList
class PairRule(Enum):
    ESCAPE = auto()  # e.g. '\\'
    COMMENT = auto()  # e.g. '#'
    PAIR_AB = auto()  # e.g. '()', '[]', '{}'
    PAIR_AA = auto()  # e.g. '""', "''", '``'
    BLOCK_AA = auto()  # e.g. '```...```'
    BLOCK_AB = auto()  # e.g. '/* ... */'


class T:
    _Start = str
    _End = str
    _Rule = PairRule
    PairRule = t.Iterable[tuple[tuple[_Start, _End], _Rule]]
    
    _Types = PairType
    PairType = t.Union[_Types.Plain, _Types.Pair]


BUILTIN_PAIR_RULES: T.PairRule = (
    (('\\', ''), PairRule.ESCAPE),
    # (('#', ''), PairRule.COMMENT),
    # (('//', ''), PairRule.COMMENT),
    (('(', ')'), PairRule.PAIR_AB),
    (('[', ']'), PairRule.PAIR_AB),
    (('{', '}'), PairRule.PAIR_AB),
    (('`', '`'), PairRule.BLOCK_AA),
    (('"', '"'), PairRule.PAIR_AA),
    (("'", "'"), PairRule.PAIR_AA),
    (('/*', '*/'), PairRule.BLOCK_AB),
    (('"""', '"""'), PairRule.BLOCK_AA),
    (("'''", "'''"), PairRule.BLOCK_AA),
)


class Scanner:
    
    def __init__(self, pair_rules: T.PairRule = BUILTIN_PAIR_RULES):
        from collections import defaultdict
        self._rules = {x[0][0]: x[1] for x in pair_rules}
        #   dict[str start, rule]
        self._pairs = dict(x[0] for x in pair_rules)
        #   dict[str start, str end]
        self._pairs_r = {v: k for k, v in self._pairs.items()}
        assert len(self._pairs) == len(self._pairs_r), (
            'text scanner does not support ambiguous pair rules, for example: '
            '`[` matches `]` while also `{` matches `]`!'
        )
        self._pair_initials = defaultdict(lambda : {
            'possible_symbols': [],
            'possible_rules': [],
        })
        #   {str initial_character: [rule, ...], ...}
        self._pair_starts = defaultdict(list)  # delete?
        self._pair_ends = defaultdict(list)  # delete?
        
        for (start, end), rule in pair_rules:
            self._pair_initials[start[0]]['possible_symbols'].append(start)
            self._pair_initials[start[0]]['possible_rules'].append(rule)
            for i in range(len(start)):
                self._pair_starts[start[:i + 1]].append(rule)
            for i in range(len(end)):
                self._pair_ends[end[:i + 1]].append(rule)
        ''' e.g.
            self._pair_starts = {
                '"': [PairRule.PAIR_AA, PairRule.BLOCK_AA],
                '""': [PairRule.BLOCK_AA],
                '"""': [PairRule.BLOCK_AA],
                ...
            }
        '''
    
    def scan(self, text: str):
        consumed = ''
        ctx = Context()
        goto_colx: int = 0
        pairs_scope = {}  # dict[str start, tuple[int colx_start, int colx_end]]
        wait_list = {
            'stack': [],  # list[str expect_end]
            #   the latest is in the first place. (we will use `insert` to add
            #   element into it.)
            'related': {},  # dict[str expect_end, int colx_of_start]
        }
        
        for rowx, line in enumerate(text.splitlines()):
            ctx.feed_line(line)
            
            for colx, char in enumerate(line):
                if colx < goto_colx:
                    continue
                if ctx.stage == ContextStage.PLAIN:
                    if x := self._pair_initials.get(char):
                        final_symbol = ''
                        for symbol in sorted(x['possible_symbols']):
                            if len(symbol) == 1:
                                final_symbol = symbol
                            else:
                                if line[colx : colx + len(symbol)] == symbol:
                                    final_symbol = symbol
                        if final_symbol:
                            rule = self._rules[final_symbol]
                            if rule == PairRule.ESCAPE:
                                goto_colx = colx + 1
                                continue
                            elif rule == PairRule.COMMENT:
                                goto_colx = len(line)
                                continue
                            elif rule == PairRule.PAIR_AB:
                                pass
                            
                            
                            ctx.stage = ContextStage.PAIR_START_DONE
                            symbol_end = self._pairs[final_symbol]
                            wait_list['stack'].insert(0, symbol_end)
                            wait_list['related'][symbol_end] = colx
                            goto_colx = colx + len(final_symbol)
                            continue
                        else:
                            consumed += char
                            continue
                    else:
                        consumed += char
                        continue
                elif ctx.stage == ContextStage.PAIR_START_DONE:
                    assert wait_list['stack']
                    for expect_end in wait_list['stack']:
                        pass
                    

# noinspection PyArgumentList
class ContextStage(Enum):
    PLAIN = auto()
    PAIRING_START = auto()
    PAIR_START_DONE = auto()
    PAIRING_END = auto()


class Context:
    stage: ContextStage = ContextStage.PLAIN
    start: str
    end: str
    _line: str
    
    def feed_line(self, line: str):
        self._line = line
