import use
from hypothesis import assume, example, given
from hypothesis import strategies as st
from pytest import fixture, mark, raises, skip

tagging = use(use.Path("../tagger.py"))
text = use(use.Path("../text_tools.py"))


def test_tokenizer():
    assert tagging.tokenize("Hello, world!") == ["hello", ",", "world", "!"]


def test_build_bot_msg():
    assert text.build_bot_msg("hello world :)", {}) == "hello world : )"
