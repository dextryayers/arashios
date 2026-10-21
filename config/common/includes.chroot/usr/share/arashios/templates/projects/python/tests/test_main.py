"""Uji dasar untuk @NAME@."""

from @NAME@.main import build_parser


def test_parser_available() -> None:
    assert build_parser().prog == "@NAME@"
