from re import DOTALL, IGNORECASE, Pattern, compile
from typing import Any, Union
import demoji
import logging
from __main__ import *
import re

log = logging.getLogger(__name__)

FLAGS = DOTALL | IGNORECASE

EMOJI_REGEX: Pattern = compile(":([^: ][^:]*[^: ]):", FLAGS)
URL_REGEX: Pattern = compile("(https?://)([a-z]+)([^a-z ,;.]+)", FLAGS)
URL_SENTENCE_REGEX: Pattern = compile("\\s*(https?://)([^ ]*?)([, :;]|$)\\s*", FLAGS)


def repeated_sub(pattern: Pattern, replacement: str, text: str) -> str:
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
    log.debug("translate_emojis(text=%r) returns %r", text, new_text)
  return new_text


def translate_urls(text: str) -> str:
  words = re.subn(r"https?://|www|\.[a-zA-Z0-9_]+/|[^a-zA-Z]+", " ", text)[0].split()
  words2 = list(
    filter(
      lambda i: len(i) > 2,
      map(
        str.lower,
        filter(
          None,
          re.split(
            "(?:[._]+)|(?=[^a-zA-Z]|(?<=[a-z])(?=[A-Z]))", " ".join(words)
          ),
        ),
      ),
    )
  )
  new_text = " ".join(" ".join(words2).split())
  if text != new_text:
    log.debug("translate_urls(text=%r) returns %r", text, new_text)
  return new_text
def norm_text(s):
  from pathlib import Path
  import json, functools, itertools

  mp = {
    k.lower(): v
    for k, v in functools.reduce(
      list.__add__,
      [
        *itertools.chain(
          list(json.loads(p.read_bytes()).items())
          for p in Path.cwd().glob("**/contractions.json")
        )
      ],
      [],
    )
  }
  [
    s := re.compile(rf"\b{re.escape(k)}\b", re.DOTALL | re.IGNORECASE).subn(v, s)[0]
    for k, v in mp.items()
  ]
  words = s.split()
  best = sorted(
    [
      (idx, w, k, v, d)
      for idx, w, k, v, d in [
        (idx, word, k, v, Levenshtein.distance(word, k.lower()))
        for idx, word in enumerate(map(str.lower, words))
        for k, v in mp.items()
      ]
      if d < 2
      and w not in mp.values()
      and w.lower() not in mp.values()
      and w.lower().capitalize() not in mp.values()
      and w.lower() != k.lower()
      and not set(w.lower().split()).intersection(v.lower().split())
    ],
    key=lambda i: i[-1],
  )
  [
    words.__setitem__(idx, v)
    for idx, w, k, v, d in best
    if words[idx].lower() == w.lower()
  ]
  return " ".join(words)
