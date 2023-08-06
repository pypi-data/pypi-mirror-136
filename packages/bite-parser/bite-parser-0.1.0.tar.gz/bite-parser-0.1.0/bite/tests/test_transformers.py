import pytest

from bite.io import ParserBuffer
from bite.parsers import CharacterSet, Literal, ParsedLiteral
from bite.tests.mock_reader import MockReader
from bite.transformers import (
    OnlyValue,
    ParsedTransform,
    Suppress,
    Transform,
    TransformValue,
)


def test_parsed_transform():
    subtree = ParsedLiteral("literal", b"LITERAL", 0, 7)

    def transform(arg):
        assert arg == subtree
        return "transformed value"

    parsed_transform = ParsedTransform("name", subtree, transform)
    assert parsed_transform.name == "name"
    assert parsed_transform.value == "transformed value"
    assert parsed_transform.start_loc == 0
    assert parsed_transform.end_loc == 7


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_buf,grammar,expected_value",
    [
        # Suppress
        (
            b"LITERAL",
            Suppress(Literal(b"LITERAL", name="literal")),
            None,
        ),
        # Transform
        (
            b"42",
            Transform(Literal(b"42"), lambda parse_tree: int(parse_tree.value)),
            42,
        ),
        # TransformValue
        (
            b"42",
            TransformValue(Literal(b"42"), int),
            42,
        ),
        # OnlyValue
        (
            b"[3]",
            OnlyValue(
                Suppress(Literal(b"["))
                + CharacterSet(b"0123456789")
                + Suppress(Literal(b"]"))
            ),
            b"3",
        ),
    ],
)
async def test_successful_parsing(input_buf, grammar, expected_value):
    buffer = ParserBuffer(MockReader(input_buf))
    parse_tree = await grammar.parse(buffer)
    assert parse_tree.value == expected_value


@pytest.mark.asyncio
async def test_unsuccessful_only_value_transform():
    buffer = ParserBuffer(MockReader(b"AA"))

    grammar0 = OnlyValue(Suppress(Literal(b"A"))[2])
    with pytest.raises(ValueError):
        _ = (await grammar0.parse(buffer)).value

    grammar1 = OnlyValue(Literal(b"A")[2])
    with pytest.raises(ValueError):
        _ = (await grammar1.parse(buffer)).value
