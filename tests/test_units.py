import use
from hypothesis import assume, example, given
from hypothesis import strategies as st
from pytest import fixture, mark, raises, skip

tagging = use(use.Path("../tagger.py"))


def test_tokenizer():
    assert tagging.tokenize("Hello, world!") == ["hello", ",", "world", "!"]
