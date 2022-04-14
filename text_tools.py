from re import DOTALL, IGNORECASE, Pattern, compile
from typing import Any, Union
import demoji
import logging
from __main__ import *
import re
log = logging.getLogger(__name__)

FLAGS = DOTALL | IGNORECASE

EMOJI_REGEX: Pattern = compile(
  ":([^: ][^:]*[^: ]):",
  FLAGS
)
URL_REGEX: Pattern = compile(
  "(https?://)([a-z]+)([^a-z ,;.]+)",
  FLAGS
)
URL_SENTENCE_REGEX: Pattern = compile(
  "\\s*(https?://)([^ ]*?)([, :;]|$)\\s*",
  FLAGS
)

def repeated_sub(
  pattern: Pattern,
  replacement: str,
  text: str
) -> str:
  prev = ""
  while text != prev:
    prev = text
    text, count = pattern.subn(replacement, text)
  return text


def translate_emojis(text: str) -> str:
 new_text = repeated_sub(EMOJI_REGEX, " \\1 ", text)
 new_text = new_text.split("]")[-1]
 new_text = new_text.strip("\n: ,")
 new_text = demoji.replace(new_text)
 new_text = repeated_sub(EMOJI_REGEX, " \\1 ", new_text)
 if text != new_text:
   log.debug(
     "translate_emojis(text=%r) returns %r",
     text, new_text
   )
 return new_text


def translate_urls(text: str) -> str:
  words = re.subn(r"https?://|www|\.[a-zA-Z0-9_]+/|[^a-zA-Z]+", " ", text)[0].split()
  words2 = list( filter(lambda i: len(i) > 2, map( str.lower, filter( None, re.split("(?:[._]+)|(?=[^a-zA-Z]|(?<=[a-z])(?=[A-Z]))", " ".join(words)), ), ) ) )
  new_text = " ".join(" ".join(words2).split())
  if text != new_text:
    log.debug(
      "translate_urls(text=%r) returns %r",
      text, new_text
    )
  return new_text