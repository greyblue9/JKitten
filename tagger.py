from functools import lru_cache
import spacy
from spacy.lang.en import English

tag_meanings = {
  "CC":  ("conjunction", "coordinating"),
  "CD":  ("numeral", "cardinal"),
  "DT":  ("determiner",),
  "EX":  ("existential there"),
  "IN":  (("preposition",), ("conjunction", "subordinating")),
  "JJ":  (("adjective",), ("numeral", "ordinal")),
  "JJR": ("adjective", "comparative"),
  "JJS": ("adjective", "superlative"),
  "LS":  ("list item marker",),
  "MD":  ("modal auxiliary",),
  "NN":  ("noun", "common", (("singular",), ("mass",))),
  "NNP": ("noun", "proper", "singular"),
  "NNS": ("noun", "common", "plural"),
  "PDT": ("pre-determiner",),
  "POS": ("genitive marker",),
  "PRP": ("pronoun", "personal"),
  "RB":  ("adverb",),
  "RBR": ("adverb", "comparative"),
  "RBS": ("adverb", "superlative"),
  "RP":  ("particle",),
  "TO":  ("marker", (("preposition",), ("infinitive",))),
  "UH":  ("interjection",),
  "VB":  ("verb", "base form"),
  "VBD": ("verb", "past tense"),
  "VBG": ("verb", (("present participle",), ("gerund",))),
  "VBN": ("verb", "past participle"),
  "VBP": ("verb", "present tense", "not 3rd person singular"),
  "VBZ": ("verb", "present tense", "3rd person singular"),
  "WDT": ("WH-determiner",),
  "WP":  ("WH-pronoun",),
  "WRB": ("WH-adverb",)
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
    for idx, tup in enumerate(meanings):
      if isinstance(tup[0], tuple):
        for t in tup:
          cur.append(t[0] if isinstance(t[0], str) else t)
      else:
        cur.append(tup)
    yield word, tuple(cur)

@lru_cache
def get_nlp(name: str="en_core_web_lg") -> English:
  import spacy
  return spacy.load("en_core_web_lg")

def parse_text(text: str):
  d = get_nlp()(text)
  sents = list(d.sents)
  seen = set()
  for sent in sents:
    toks = list(sent)
    toks_clean = list(
      t for t in d if not t.is_stop and not t.is_punct
    )
    if sent.ents:
      yield from map(str, sent.ents)
    
    subtrees = [list(t.subtree) for t in toks_clean]
    longest_subtrees = sorted(
      subtrees, key=len, reverse=True
    )
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
    for search_seq in search_seqs:
      if any(tok_strs[i: i+len(search_seq)] == search_seq 
        for i in range(0, len(tok_strs)-len(search_seq))
      ):
        found.append(search_seq)
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
          if word in (
            "who", "what", "when", "where", "why", "how"
          ):
            question = True
          if word in ("how", "'s"):
            next_word = words[widx+1: widx+2]
            if next_word:
              attributes.append(next_word[0])

  if contains_seqs(text, ("what", "is")):
    question = True
    person = False
  if contains_seqs(text, ("who", "is")):
    question = True
    person = True
  if not attributes:
    attributes.extend(
      [
        wd 
        for wd,pos in tagged
        if pos == "JJ" 
        and not any(
          wd in ent.split() for ent in entities
        )
      ]
    )
  return {
    "tagged": tagged,
    "items": items,
    "question": question,
    "person": person,
    "entities": tuple(entities),
    "attributes": tuple(attributes),
    "clauses": tuple(clauses),
  }

