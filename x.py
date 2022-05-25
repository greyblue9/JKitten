from functools import lru_cache
import spacy
from spacy.lang.en import English
import nltk
from nltk import word_tokenize
from collections import Counter
from itertools import chain
from logging import getLogger
log = getLogger(__name__)

# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")

@lru_cache
def get_nlp(name: str = "en_core_web_md") -> English:
  import spacy
  return spacy.load(name)


tag_meanings = {
  "CC": ("conjunction", "coordinating"),
  "CD": ("numeral", "cardinal"),
  "DT": ("determiner",),
  "EX": ("existential there"),
  "IN": (("preposition",), ("conjunction", "subordinating")),
  "JJ": (("adjective",), ("numeral", "ordinal")),
  "JJR": ("adjective", "comparative"),
  "JJS": ("adjective", "superlative"),
  "LS": ("list item marker",),
  "MD": ("modal auxiliary",),
  "NN": ("noun", "common", (("singular",), ("mass",))),
  "NNP": ("noun", "proper", "singular"),
  "NNS": ("noun", "common", "plural"),
  "PDT": ("pre-determiner",),
  "POS": ("genitive marker",),
  "PRP": ("pronoun", "personal"),
  "RB": ("adverb",),
  "RBR": ("adverb", "comparative"),
  "RBS": ("adverb", "superlative"),
  "RP": ("particle",),
  "TO": ("marker", (("preposition",), ("infinitive",))),
  "UH": ("interjection",),
  "VB": ("verb", "base form"),
  "VBD": ("verb", "past tense"),
  "VBG": ("verb", (("present participle",), ("gerund",))),
  "VBN": ("verb", "past participle"),
  "VBP": ("verb", "present tense", "not 3rd person singular"),
  "VBZ": ("verb", "present tense", "3rd person singular"),
  "WDT": ("WH-determiner",),
  "WP": ("WH-pronoun",),
  "WRB": ("WH-adverb",),
}


def tag_sentence(sentence, describe=False):
  from __main__ import pos_tag

  tagged = pos_tag(word_tokenize(sentence))
  if not describe:
    yield from tagged
    return
  for word, tag in tagged:
    cur = []
    meanings = tag_meanings.get(tag)
    if meanings is None:
      cur = [tag]
      yield word, tuple(cur)
      continue
    for tup in meanings:
      if isinstance(tup[0], tuple):
        cur.extend(t[0] if isinstance(t[0], str) else t for t in tup)
      else:
        cur.append(tup)
    yield word, tuple(cur)


def parse_text(text: str):
  d = get_nlp()(text)
  sents = list(d.sents)
  seen = set()
  for sent in sents:
    toks = list(sent)
    toks_clean = [t for t in d if not t.is_stop and not t.is_punct]
    if sent.ents:
      yield from map(str, sent.ents)

    subtrees = [list(t.subtree) for t in toks_clean]
    longest_subtrees = sorted(subtrees, key=len, reverse=True)
    for subtree in longest_subtrees:
      if all(w in seen for w in subtree):
        continue
      if any(subtree[0] in ss for ss in seen):
        continue
      seen.add(tuple(subtree))
      yield " ".join(tuple(map(str, subtree)))


def contains_seqs(text, *search_seqs):
  found = []
  d = get_nlp()(text.lower())
  for sent in d.sents:
    tok_strs = tuple(map(str, sent))
    found.extend(
        search_seq for search_seq in search_seqs
        if any(tok_strs[i:i + len(search_seq)] == search_seq
               for i in range(len(tok_strs) - len(search_seq))))
  return tuple(found)


def categorize(text: str):
  log.info("categorize: text=%r", text)
  from __main__ import pos_tag
  parsed = list(parse_text(text))
  log.info("categorize: parsed=%r", parsed)
  items = parsed
  log.info("categorize: items=%r", items)

  ctr = Counter(items)
  log.info("categorize: ctr=%r", ctr)
  tokenized = word_tokenize(text.lower())
  log.info("categorize: tokenized=%r", tokenized)
  tagged = pos_tag(text.lower())
  log.info("categorize: text=%r", tagged)

  question = False
  person = False
  attributes = []
  entities = []
  clauses = []
  for wd, pos in tagged:
    if wd.lower().split("'")[0] in ("who", "what", "when", "where", "why", "how"):
      question = True

  for item, count in ctr.most_common():
    if count > 1:
      entities.append(item)
    else:
      clauses.append(item)
      words = item.lower().split()
      for widx, word in enumerate(words):
        if widx == 0:
          if word in ("who", "what", "when", "where", "why", "how"):
            question = True
          if word in ("how", "'s"):
            if next_word := words[widx + 1:widx + 2]:
              attributes.append(next_word[0])

  if (contains_seqs(text, ("what", "is")) or contains_seqs(text, ("what", "was")) or contains_seqs(text, ("what", "were")) or contains_seqs(text, ("who", "is")) or contains_seqs(text, ("who", "was")) or contains_seqs(text, ("who", "were")) or contains_seqs(text, ("where", "is")) or contains_seqs(text, ("where", "was")) or contains_seqs(text, ("where", "were")) or contains_seqs(text, ("when", "is")) or contains_seqs(text, ("when", "are")) or contains_seqs(text, ("when", "were")) or contains_seqs(text, ("how", "do")) or contains_seqs(text, ("how", "does"))):
    question = True
  if "you" in text.lower():
    person = True
  if contains_seqs(text, ("who", "is")):
    question = True
    person = True
  if not attributes:
    attributes.extend([
        wd for wd, pos in tagged
        if pos == "JJ" and all(wd not in ent.split() for ent in entities)
    ])
  return {
    "tagged": tagged,
    "items": items,
    "question": question,
    "person": person,
    "entities": tuple(entities),
    "attributes": tuple(attributes),
    "clauses": tuple(clauses),
    "proper_noun": next(iter(chain((
      wd
      for wd, pos in tagged
      if pos in ("NN", "NNS", "NNP") 
    ), (None,))))
  }
from functools import lru_cache
import spacy
from spacy.lang.en import English
import nltk

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


@lru_cache
def get_nlp(name: str = "en_core_web_md") -> English:
  import spacy

  return spacy.load(name)


tag_meanings = {
  "CC": ("conjunction", "coordinating"),
  "CD": ("numeral", "cardinal"),
  "DT": ("determiner",),
  "EX": ("existential there"),
  "IN": (("preposition",), ("conjunction", "subordinating")),
  "JJ": (("adjective",), ("numeral", "ordinal")),
  "JJR": ("adjective", "comparative"),
  "JJS": ("adjective", "superlative"),
  "LS": ("list item marker",),
  "MD": ("modal auxiliary",),
  "NN": ("noun", "common", (("singular",), ("mass",))),
  "NNP": ("noun", "proper", "singular"),
  "NNS": ("noun", "common", "plural"),
  "PDT": ("pre-determiner",),
  "POS": ("genitive marker",),
  "PRP": ("pronoun", "personal"),
  "RB": ("adverb",),
  "RBR": ("adverb", "comparative"),
  "RBS": ("adverb", "superlative"),
  "RP": ("particle",),
  "TO": ("marker", (("preposition",), ("infinitive",))),
  "UH": ("interjection",),
  "VB": ("verb", "base form"),
  "VBD": ("verb", "past tense"),
  "VBG": ("verb", (("present participle",), ("gerund",))),
  "VBN": ("verb", "past participle"),
  "VBP": ("verb", "present tense", "not 3rd person singular"),
  "VBZ": ("verb", "present tense", "3rd person singular"),
  "WDT": ("WH-determiner",),
  "WP": ("WH-pronoun",),
  "WRB": ("WH-adverb",),
}


def tag_sentence(sentence, describe=False):
  from nltk import pos_tag, word_tokenize

  tagged = pos_tag(word_tokenize(sentence))
  if not describe:
    yield from tagged
    return
  for word, tag in tagged:
    cur = []
    meanings = tag_meanings.get(tag)
    if meanings is None:
      cur = [tag]
      yield word, tuple(cur)
      continue
    for tup in meanings:
      if isinstance(tup[0], tuple):
        cur.extend(t[0] if isinstance(t[0], str) else t for t in tup)
      else:
        cur.append(tup)
    yield word, tuple(cur)


@lru_cache
def get_nlp(name: str = "en_core_web_md") -> English:
  import spacy

  return spacy.load("en_core_web_md")


def parse_text(text: str):
  d = get_nlp()(text)
  sents = list(d.sents)
  seen = set()
  for sent in sents:
    toks = list(sent)
    toks_clean = [t for t in d if not t.is_stop and not t.is_punct]
    if sent.ents:
      yield from map(str, sent.ents)

    subtrees = [list(t.subtree) for t in toks_clean]
    longest_subtrees = sorted(subtrees, key=len, reverse=True)
    for subtree in longest_subtrees:
      if all(w in seen for w in subtree):
        continue
      if any(subtree[0] in ss for ss in seen):
        continue
      seen.add(tuple(subtree))
      yield " ".join(tuple(map(str, subtree)))


def contains_seqs(text, *search_seqs):
  found = []
  d = get_nlp()(text.lower())
  for sent in d.sents:
    tok_strs = tuple(map(str, sent))
    found.extend(
        search_seq for search_seq in search_seqs
        if any(tok_strs[i:i + len(search_seq)] == search_seq
               for i in range(len(tok_strs) - len(search_seq))))
  return tuple(found)


def categorize(text: str):
  items = list(parse_text(text))
  from collections import Counter

  ctr = Counter(items)
  from nltk import pos_tag, word_tokenize

  tagged = pos_tag(word_tokenize(text.lower()))
  question = False
  person = False
  attributes = []
  entities = []
  clauses = []
  for item, count in ctr.most_common():
    if count > 1:
      entities.append(item)
    else:
      clauses.append(item)
      words = item.lower().split()
      for widx, word in enumerate(words):
        if widx == 0:
          if word in ("who", "what", "when", "where", "why", "how"):
            question = True
          if word in ("how", "'s"):
            if next_word := words[widx + 1:widx + 2]:
              attributes.append(next_word[0])

  if contains_seqs(text, ("what", "is")):
    question = True
    person = False
  if contains_seqs(text, ("who", "is")):
    question = True
    person = True
  if not attributes:
    attributes.extend([
        wd for wd, pos in tagged
        if pos == "JJ" and all(wd not in ent.split() for ent in entities)
    ])
  return {
    "tagged": tagged,
    "items": items,
    "question": question,
    "person": person,
    "entities": tuple(entities),
    "attributes": tuple(attributes),
    "clauses": tuple(clauses),
  }
from functools import lru_cache
import spacy
from spacy.lang.en import English
import nltk

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


@lru_cache
def get_nlp(name: str = "en_core_web_md") -> English:
  import spacy

  return spacy.load(name)


tag_meanings = {
  "CC": ("conjunction", "coordinating"),
  "CD": ("numeral", "cardinal"),
  "DT": ("determiner",),
  "EX": ("existential there"),
  "IN": (("preposition",), ("conjunction", "subordinating")),
  "JJ": (("adjective",), ("numeral", "ordinal")),
  "JJR": ("adjective", "comparative"),
  "JJS": ("adjective", "superlative"),
  "LS": ("list item marker",),
  "MD": ("modal auxiliary",),
  "NN": ("noun", "common", (("singular",), ("mass",))),
  "NNP": ("noun", "proper", "singular"),
  "NNS": ("noun", "common", "plural"),
  "PDT": ("pre-determiner",),
  "POS": ("genitive marker",),
  "PRP": ("pronoun", "personal"),
  "RB": ("adverb",),
  "RBR": ("adverb", "comparative"),
  "RBS": ("adverb", "superlative"),
  "RP": ("particle",),
  "TO": ("marker", (("preposition",), ("infinitive",))),
  "UH": ("interjection",),
  "VB": ("verb", "base form"),
  "VBD": ("verb", "past tense"),
  "VBG": ("verb", (("present participle",), ("gerund",))),
  "VBN": ("verb", "past participle"),
  "VBP": ("verb", "present tense", "not 3rd person singular"),
  "VBZ": ("verb", "present tense", "3rd person singular"),
  "WDT": ("WH-determiner",),
  "WP": ("WH-pronoun",),
  "WRB": ("WH-adverb",),
}


def tag_sentence(sentence, describe=False):
  from nltk import pos_tag, word_tokenize

  tagged = pos_tag(word_tokenize(sentence))
  if not describe:
    yield from tagged
    return
  for word, tag in tagged:
    cur = []
    meanings = tag_meanings.get(tag)
    if meanings is None:
      cur = [tag]
      yield word, tuple(cur)
      continue
    for tup in meanings:
      if isinstance(tup[0], tuple):
        cur.extend(t[0] if isinstance(t[0], str) else t for t in tup)
      else:
        cur.append(tup)
    yield word, tuple(cur)


@lru_cache
def get_nlp(name: str = "en_core_web_md") -> English:
  import spacy

  return spacy.load("en_core_web_md")


def parse_text(text: str):
  d = get_nlp()(text)
  sents = list(d.sents)
  seen = set()
  for sent in sents:
    toks = list(sent)
    toks_clean = [t for t in d if not t.is_stop and not t.is_punct]
    if sent.ents:
      yield from map(str, sent.ents)

    subtrees = [list(t.subtree) for t in toks_clean]
    longest_subtrees = sorted(subtrees, key=len, reverse=True)
    for subtree in longest_subtrees:
      if all(w in seen for w in subtree):
        continue
      if any(subtree[0] in ss for ss in seen):
        continue
      seen.add(tuple(subtree))
      yield " ".join(tuple(map(str, subtree)))


def contains_seqs(text, *search_seqs):
  found = []
  d = get_nlp()(text.lower())
  for sent in d.sents:
    tok_strs = tuple(map(str, sent))
    found.extend(
        search_seq for search_seq in search_seqs
        if any(tok_strs[i:i + len(search_seq)] == search_seq
               for i in range(len(tok_strs) - len(search_seq))))
  return tuple(found)


def categorize(text: str):
  items = list(parse_text(text))
  from collections import Counter

  ctr = Counter(items)
  from nltk import pos_tag, word_tokenize

  tagged = pos_tag(word_tokenize(text.lower()))
  question = False
  person = False
  attributes = []
  entities = []
  clauses = []
  for item, count in ctr.most_common():
    if count > 1:
      entities.append(item)
    else:
      clauses.append(item)
      words = item.lower().split()
      for widx, word in enumerate(words):
        if widx == 0:
          if word in ("what", "who", "when", "where", "how", "why"):
            question = True
          if word in ("how", "'s"):
            if next_word := words[widx + 1:widx + 2]:
              attributes.append(next_word[0])

  if contains_seqs(text, ("what", "is")):
    question = True
    person = False
  if contains_seqs(text, ("what", "was")):
    question = True
    person = False
  if contains_seqs(text, ("what", "were")):
    question = True
    person = False
  if contains_seqs(text, ("what", "will")):
    question = True
    person = False
  if contains_seqs(text, ("what", "has")):
    question = True
    person = False
  if contains_seqs(text, ("what", "had")):
    question = True

  if contains_seqs(text, ("who", "is")):
    question = True
    person = False
  if contains_seqs(text, ("who", "was")):
    question = True
    person = False
  if contains_seqs(text, ("who", "were")):
    question = True
    person = False
  if contains_seqs(text, ("who", "will")):
    question = True
    person = False
  if contains_seqs(text, ("who", "has")):
    question = True
    person = False
  if contains_seqs(text, ("who", "had")):
    question = True
    person = False

  if not attributes:
    attributes.extend([
        wd for wd, pos in tagged
        if pos == "JJ" and all(wd not in ent.split() for ent in entities)
    ])
  return {
    "tagged": tagged,
    "items": items,
    "question": question,
    "person": person,
    "entities": tuple(entities),
    "attributes": tuple(attributes),
    "clauses": tuple(clauses),
  }