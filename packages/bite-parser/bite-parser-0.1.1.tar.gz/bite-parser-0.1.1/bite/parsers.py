from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, TypeVar

from bite.core import (
    And,
    MatchFirst,
    ParsedAnd,
    ParsedBaseNode,
    ParsedLeaf,
    ParsedMatchFirst,
    ParsedNode,
    ParsedRepeat,
    Parser,
    Repeat,
    UnmetExpectationError,
)
from bite.io import ParserBuffer

assert ParsedAnd  # re-export
assert ParsedMatchFirst  # re-export

T = TypeVar("T", covariant=True)
V = TypeVar("V", covariant=True)

ParsedLiteral = ParsedLeaf[bytes]


class Literal(Parser[bytes, bytes]):
    def __init__(self, literal: bytes, *, name: str = None):
        super().__init__(name if name else str(literal))
        self.literal = literal

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedLiteral:
        end_loc = loc + len(self.literal)
        peek = await buf.get(slice(loc, end_loc))
        if peek == self.literal:
            return ParsedLiteral(self.name, self.literal, loc, end_loc)
        else:
            raise UnmetExpectationError(self, loc)


class CaselessLiteral(Parser[bytes, bytes]):
    def __init__(self, literal: bytes, *, name: str = None):
        super().__init__(name if name else str(literal))
        self.literal = literal
        self._lowercased_literal = self.literal.lower()

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedLiteral:
        end_loc = loc + len(self.literal)
        peek = await buf.get(slice(loc, end_loc))
        if peek.lower() == self._lowercased_literal:
            return ParsedLiteral(self.name, self.literal, loc, end_loc)
        else:
            raise UnmetExpectationError(self, loc)


ParsedCharacterSet = ParsedLeaf[bytes]


class CharacterSet(Parser[bytes, bytes]):
    def __init__(
        self, charset: Iterable[int], *, invert: bool = False, name: str = None
    ):
        super().__init__(name if name else f"CharacterSet({charset})")
        self.charset = frozenset(charset)
        self.invert = invert

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedCharacterSet:
        char = await buf.get(loc)
        if len(char) == 1 and (char[0] in self.charset) != self.invert:
            return ParsedCharacterSet(self.name, char, loc, loc + 1)
        else:
            raise UnmetExpectationError(self, loc)


ParsedFixedByteCount = ParsedLeaf[bytes]


class FixedByteCount(Parser[bytes, bytes]):
    def __init__(self, count: int, *, name: str = None):
        super().__init__(name if name else f"FixedByteCount({count})")
        self.count = count

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedFixedByteCount:
        read_bytes = await buf.get(slice(loc, loc + self.count))
        if len(read_bytes) == self.count:
            return ParsedFixedByteCount(
                self.name, read_bytes, loc, loc + len(read_bytes)
            )
        else:
            raise UnmetExpectationError(self, loc)


ParsedZeroOrMore = ParsedRepeat


class ZeroOrMore(Repeat[T, V]):
    def __init__(self, parser: Parser[T, V], *, name: str = None):
        super().__init__(parser, min_repeats=0, name=name)


ParsedOneOrMore = ParsedRepeat


class OneOrMore(Repeat[T, V]):
    def __init__(self, parser: Parser[T, V], *, name: str = None):
        super().__init__(parser, min_repeats=1, name=name)


ParsedOpt = ParsedRepeat


class Opt(Repeat[T, V]):
    def __init__(self, parser: Parser[T, V], *, name: str = None):
        super().__init__(parser, min_repeats=0, max_repeats=1, name=name)


@dataclass(frozen=True)
class CountedParseTree:
    count_expr: ParsedNode[Any, int]
    counted_expr: ParsedNode

    @property
    def start_loc(self) -> int:
        return self.count_expr.start_loc

    @property
    def end_loc(self) -> int:
        return self.counted_expr.end_loc


@dataclass(frozen=True)
class ParsedCounted(ParsedBaseNode[CountedParseTree], Generic[V]):
    @property
    def values(self) -> Iterable[V]:
        return self.parse_tree.counted_expr.values

    @property
    def start_loc(self) -> int:
        return self.parse_tree.start_loc

    @property
    def end_loc(self) -> int:
        return self.parse_tree.end_loc


class Counted(Parser[CountedParseTree, V]):
    def __init__(
        self,
        count_parser: Parser[Any, int],
        counted_parser_factory: Callable[[int], Parser[Any, V]],
        *,
        name: str = None,
    ):
        super().__init__(
            name if name else f"Counted({count_parser.name}, {counted_parser_factory})"
        )
        self.count_parser = count_parser
        self.counted_parser_factory = counted_parser_factory

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedCounted[V]:
        count_parse_tree = await self.count_parser.parse(buf, loc)
        values_iter = iter(count_parse_tree.values)
        try:
            count = int(next(values_iter))
        except StopIteration:
            raise ValueError("count expression did not return a value") from None
        try:
            next(values_iter)
        except StopIteration:
            counted = await self.counted_parser_factory(count).parse(
                buf, count_parse_tree.end_loc
            )
            return ParsedCounted(self.name, CountedParseTree(count_parse_tree, counted))
        else:
            raise ValueError("count expression returned more than one value")


ParsedCombine = ParsedLeaf[bytes]


class Combine(Parser[bytes, bytes]):
    def __init__(self, parser: Parser[Any, bytes], *, name: str = None):
        super().__init__(name if name else f"Combine({parser})")
        self.parser = parser

    async def parse(self, buf: ParserBuffer, loc: int = 0) -> ParsedCombine:
        parse_tree = await self.parser.parse(buf, loc)
        return ParsedCombine(
            self.name,
            b"".join(parse_tree.values),
            parse_tree.start_loc,
            parse_tree.end_loc,
        )


__all__ = [
    "And",
    "CaselessLiteral",
    "CharacterSet",
    "Combine",
    "Counted",
    "FixedByteCount",
    "Literal",
    "MatchFirst",
    "OneOrMore",
    "Opt",
    "Repeat",
    "ZeroOrMore",
]
