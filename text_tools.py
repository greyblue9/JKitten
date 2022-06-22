import logging
import re
import codecs
from tools import pipes

import demoji
import Levenshtein
from __main__ import *
from beartype import beartype

log = logging.getLogger(__name__)

FLAGS = re.DOTALL | re.IGNORECASE

EMOJI_REGEX: re.Pattern = re.compile(":([^: ][^:]*[^: ]):", FLAGS)
URL_REGEX: re.Pattern = re.compile("(https?://)([a-z]+)([^a-z ,;.]+)", FLAGS)
URL_SENTENCE_REGEX: re.Pattern = re.compile("\\s*(https?://)([^ ]*?)([, :;]|$)\\s*", FLAGS)

@beartype
def repeated_sub(pattern: re.Pattern, replacement: str, text: str) -> str:
    prev = ""
    while text != prev:
        prev = text
        text, count = pattern.subn(replacement, text)
    return text


@beartype
def translate_emojis(text: str) -> str:
    new_text = repeated_sub(EMOJI_REGEX, " \\1 ", text)
    new_text = new_text.split("]")[-1]
    new_text = new_text.strip("\n: ,")
    new_text = demoji.replace(new_text)
    new_text = repeated_sub(EMOJI_REGEX, " \\1 ", new_text)
    if text != new_text:
        log.debug("translate_emojis(text=%r) returns %r", text, new_text)
    return new_text

@beartype
def translate_urls(text: str) -> str:
    words = re.subn(r"https?://|www|\.[a-zA-Z0-9_]+/|[^a-zA-Z]+", " ", text)[0].split()
    words2 = list(
        filter(
            lambda i: len(i) > 2,
            map(
                str.lower,
                filter(
                    None,
                    re.split("(?:[._]+)|(?=[^a-zA-Z]|(?<=[a-z])(?=[A-Z]))", " ".join(words)),
                ),
            ),
        )
    )
    new_text = " ".join(" ".join(words2).split())
    if text != new_text:
        log.debug("translate_urls(text=%r) returns %r", text, new_text)
    return new_text


def norm_text(s):
    log.debug("norm_text: s=%r", s)
    import functools
    import itertools
    import json
    from pathlib import Path

    mp = {
        k.lower(): v
        for k, v in functools.reduce(
            list.__add__,
            [
                *itertools.chain(
                    list(json.loads(p.read_bytes()).items()) for p in Path.cwd().glob("**/contractions.json")
                )
            ],
            [],
        )
    }
    [s := re.compile(rf"\b{re.escape(k)}\b", re.DOTALL | re.IGNORECASE).subn(v, s)[0] for k, v in mp.items()]
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
            and len(w) == len(k) + 1
        ],
        key=lambda i: i[-1],
    )
    [
        words.__setitem__(idx, v)
        for idx, w, k, v, d in best[:0]
        if words[idx].lower() == w.lower() and words[idx][:2].lower() == w[:2].lower()
    ]
    r = " ".join(words)
    r = re.compile(
        "(i am|my name's|my name is|i'm|call me|i'm called|i am called|calls me|(?: am| me| name[s i']*|call[a-z*])) ([A-Z][a-zA-Z*])(?=$|[^a-zA-Z])",
        re.DOTALL,
    ).sub("\\1 Alice", r)

    log.debug("norm_text(s=%r): returning r=%r", s, r)
    return r



def clean_response(s, bot_message=None):
    if bot_message and re.subn("[^a-z]+", "", s.lower()) == re.subn("[^a-z]+", "", bot_message.lower()):
        return ""
    s = next(iter(sorted(s.split(" \xb7 "), key=len, reverse=True)))
    s2 = re.subn(
        "([.,!;?]) *([A-Z][a-z]{2}) [1-3][0-9]?, [12][0-9]{3}[^A-Za-z]*",
        "\\1 \n",
        re.subn(
            "(^|[.,;?!]) *i('[a-z]+|) ",
            "\\1 I\\2 ",
            re.subn("(?<=[a-zA-Z])(([!,?;])[.]|([.])) *($|[A-Za-z])", "\\2\\3 \\4", s.replace("&nbsp;", " "))[
                0
            ],
        )[0],
    )[0]
    return "  ".join(
        {
            (s.strip()[0].upper() + s.strip()[1:]): None
            for s in re.split(
                "(?<=[.!?])[\t\n ]*(?=[a-zA-Z][^.,;?]{3,})",
                re.subn(
                    "([.,!;?]) *([A-Z][a-z]{2}) [1-3][0-9]?, [12][0-9]{3}[^A-Za-z]*",
                    "\\1 \n",
                    re.subn(
                        "(^|[.,;?!]) *i('[a-z]+|) ",
                        "\\1 I\\2 ",
                        re.subn(
                            "(?<=[a-zA-Z])(([!,?;])[.]|([.])) *($|[A-Za-z](?=[^.!?]{4,}))", "\\2\\3 \\4", s2
                        )[0],
                    )[0],
                )[0],
            )
        }.keys()
    )


def strip_extra(s):
    print("strip_xtra(%r)" % (s,))

    escaped = codecs.unicode_escape_encode(s)[0]
    print("strip_xtra(%r): escaped=%r" % (s, escaped))

    splits = re.compile(rb"[\t ][\t ]+|\\n|\\xb7|\\xa0", re.DOTALL).split(escaped)
    ok = []
    for i in splits:
        i = i.strip()
        if re.compile(rb"^[A-Z][a-z]{2} \d+(,|$)", re.DOTALL).search(i):
            continue
        if not re.compile(rb"([A-Z]*[a-z]+|[A-Z]+|[a-z]+|[A-Z]+[a-z]*) ", re.DOTALL).search(i):
            continue
        ok.append(i)
    if not ok:
        return ""
    ordered = sorted(ok, key=len)
    longest = ordered[-1]

    s0 = codecs.unicode_escape_decode(longest)[0]
    print("strip_xtra(%r): s0=%r" % (s, s0))

    s1 = re.compile("(?<=[^a-zA-Z])'((?:[^'.]|(?<=[a-z]))'[a-z]+)(\\.?)'", re.DOTALL).sub("\\1", s0).strip()

    return re.compile("([a-z])'[a-z]*", re.DOTALL).sub("\\1", s1).strip()


def find(coll, r):
    return (
        [coll[idx + 1 :] + coll[idx : idx + 1] for idx, w in enumerate(coll) if w in r][0]
        if any(w in coll for w in r)
        else [coll]
    )


def norm_sent(k, s):
    exec(
        'for f,t in k._subbers["normal"].items(): s = re.sub(rf"\\b{re.escape(f)}\\b", t, s)',
        locals(),
    )
    return re.sub(
        r" ([^a-zA-Z0-9_])\1* *",
        "\\1",
        " ".join(
            filter(
                None,
                map(
                    str.strip,
                    re.split(
                        r"(?:(?<=[a-zA-Z0-9_]))(?=[^a-zA-Z0-9_])|(?:(?<=[^a-zA-Z0-9_]))(?=[a-zA-Z0-9_])",
                        s,
                    ),
                ),
            )
        ),
    )
