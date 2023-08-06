""" WIP
a general purpose text scanner for extracting paired snippets from text.

example:
    input:
        aaa (bbb) "ccc 'ddd' (eee)" [fff [ggg]
    output (this is a conception, not the real result):
        [
            <Plain text='aaa ', symbol='', children=[]>,
            <SinglePair text='bbb', symbol='()', children=[]>,
            <MultiplePairs text='ccc \'ddd\' (eee)', symbol='""', children=[
                <Plain text='ccc ', symbol='', children=[]>,
                <SinglePair text='ddd', symbol='\'\'', children=[]>,
                <Plain text=' ', symbol='', children=[]>,
                <SinglePair text='eee', symbol='()', children=[]>,
            ]>,
            <Plain text=' [fff', symbol='', children=[]>,
            <MultiplePairs text='ggg', symbol='[]', children=[]>,
        ]
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
    
    @dataclass
    class SinglePair:  # delete?
        text: str
        symbol: tuple[str, str]
        children: list | tuple = ()

    @dataclass
    class MultiplePairs:  # delete?
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
    PairType = t.Union[_Types.Plain, _Types.SinglePair, _Types.MultiplePairs]


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
        self._rules = pair_rules
        self._pairs = dict(x[0] for x in pair_rules)
        self._pairs_r = {v: k for k, v in self._pairs.items()}
        assert len(self._pairs) == len(self._pairs_r), (
            'text scanner does not support ambiguous pair rules, for example: '
            '`[` matches `]` while also `{` matches `]`!'
        )
        self._pair_starts = defaultdict(list)
        self._pair_ends = defaultdict(list)
        
        for (start, end), rule in pair_rules:
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
        for line in text.splitlines():
            yield from self.scan_snippet(line)

    def scan_snippet(self, snip: str) -> t.Iterator[T.PairType]:
        """
        a snippet is a piece of text, which is a single line.
        this method can be recursively called.
        """
        consumed = ''
        context = Context()
        
        possibles: list[T.PairRule]
        determined: T.PairRule
        
        pairing_pointer = 0  # del
        pairing_initial = ''  # del
        pairing_symbol = ''  # del
        pair_start_store = ''
        pair_end_store = ''
        pair_end_expect = ''
        
        def is_complete(symbol: str, is_start: bool = True) -> bool:
            if is_start:
                return symbol in self._pairs
            else:
                return symbol in self._pairs_r
        
        for char in snip:
            if context.stage == ContextStage.PLAIN:
                if char not in self._pair_starts:
                    consumed += char
                    continue
                else:
                    yield PairType.Plain(consumed)
                    consumed = ''
                    
                    context.stage = ContextStage.PAIRING_START
                    pair_start_store = ''  # reset
            
            if context.stage == ContextStage.PAIRING_START:
                pair_start_store += char
                possibles = self._pair_starts[pair_start_store]
                if len(possibles) == 1:
                    if is_complete(pair_start_store):
                        # the pair is complete.
                        context.rule = possibles[0]
                        context.stage = ContextStage.PAIR_START_DONE
                        pair_end_expect = self._pairs[pair_start_store]
                        pair_end_store = ''  # reset
                        continue
                    else:
                        continue
                pass
            
            if context.stage == ContextStage.PAIR_START_DONE:
                pair_end_store += char
                if pair_end_store in self._pairs_r:
                    # the pair match is complete.
                    yield PairType.SinglePair()
                if context.rule == PairRule.PAIR_AB:
                    end = self._pairs[pair_start_store]
                    
                if char in self._pair_starts:
                    pass
                
                if char not in self._pair_starts:
                    consumed += char
                    continue


# noinspection PyArgumentList
class ContextStage(Enum):
    PLAIN = auto()
    PAIRING_START = auto()
    PAIR_START_DONE = auto()
    PAIRING_END = auto()
    

class Context:
    stage: ContextStage = ContextStage.PLAIN
    rule: t.Optional[T.PairRule] = None
    # pair_store: str = ''
    start: str = ''
    end: str = ''
