from functools import lru_cache
import spacy
from spacy.lang.en import English
import nltk
from nltk import word_tokenize
from collections import Counter
from itertools import chain
from logging import getLogger
log = getLogger(__name__)

from functools import lru_cache
import spacy
from spacy.lang.en import English
nltk.download("wordnet")
nltk.download("brown")
nltk.download("conll2000")
nltk.download("treebank")
nltk.download('stopwords')
nltk.download('omw-1.4')
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

import spacy
from nltk.corpus import webtext, nps_chat

nlp = spacy.blank("en")
from spacy.lang.en import English
parser = English()
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

en_stop = set(nltk.corpus.stopwords.words('english'))
import pickle
from nltk import DefaultTagger, UnigramTagger, BigramTagger, TrigramTagger
from random import choice


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
    for idx, tup in enumerate(meanings):
      if isinstance(tup[0], tuple):
        for t in tup:
          cur.append(t[0] if isinstance(t[0], str) else t)
      else:
        cur.append(tup)
    yield word, tuple(cur)


def parse_text(text: str):
  d = get_nlp()(text)
  sents = list(d.sents)
  seen = set()
  for sent in sents:
    toks = list(sent)
    toks_clean = list(t for t in d if not t.is_stop and not t.is_punct)
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
    for search_seq in search_seqs:
      if any(
        tok_strs[i : i + len(search_seq)] == search_seq
        for i in range(0, len(tok_strs) - len(search_seq))
      ):
        found.append(search_seq)
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
            next_word = words[widx + 1 : widx + 2]
            if next_word:
              attributes.append(next_word[0])

  if (contains_seqs(text, ("what", "is")) or contains_seqs(text, ("what", "was")) or contains_seqs(text, ("what", "were")) or contains_seqs(text, ("who", "is")) or contains_seqs(text, ("who", "was")) or contains_seqs(text, ("who", "were")) or contains_seqs(text, ("where", "is")) or contains_seqs(text, ("where", "was")) or contains_seqs(text, ("where", "were")) or contains_seqs(text, ("when", "is")) or contains_seqs(text, ("when", "are")) or contains_seqs(text, ("when", "were")) or contains_seqs(text, ("how", "do")) or contains_seqs(text, ("how", "does"))):
    question = True
  if "you" in text.lower():
    person = True
  if contains_seqs(text, ("who", "is")):
    question = True
    person = True
  if not attributes:
    attributes.extend(
      [
        wd
        for wd, pos in tagged
        if pos == "JJ" and not any(wd in ent.split() for ent in entities)
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
    "proper_noun": next(iter(chain((
      wd
      for wd, pos in tagged
      if pos in ("NN", "NNS", "NNP") 
    ), (None,))))
  }

class SubjectTrigramTagger:

  """ Creates an instance of NLTKs TrigramTagger with a backoff
  tagger of a bigram tagger a unigram tagger and a default tagger that sets
  all words to nouns (NN)
  """

  def __init__(self, train_sents):

      """
      train_sents: trained sentences which have already been tagged.
              Currently using Brown, conll2000, and TreeBank corpuses
      """

      t0 = DefaultTagger('NN')
      t1 = UnigramTagger(train_sents, backoff=t0)
      t2 = BigramTagger(train_sents, backoff=t1)
      self.tagger = TrigramTagger(train_sents, backoff=t2)

  def __call__(self, tokens):
      return self.tagger.tag(list(tokens))

def get_tagger():   
  try:
    with open("trained_tagger.pkl", "rb") as file:
          trigram_tagger = pickle.load(file)
          return trigram_tagger
  except (FileNotFoundError, EOFError):
      pass
  train_sents = nltk.corpus.brown.tagged_sents()
  train_sents += nltk.corpus.conll2000.tagged_sents()
  train_sents += nltk.corpus.treebank.tagged_sents()
  trigram_tagger = SubjectTrigramTagger(train_sents)
  with open("trained_tagger.pkl", "wb") as file:
      pickle.dump(trigram_tagger, file)
  return trigram_tagger

trigram_tagger = get_tagger()

def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

 
def get_lemma(word):
    return WordNetLemmatizer().lemmatize(word)

def get_svo(sentence, subject):
    """Returns a dictionary containing:
    subject : the subject determined earlier
    action : the action verb of particular related to the subject
    object : the object the action is referring to
    phrase : list of token, tag pairs for that lie within the indexes of
                the variables above
    """
    subject_idx = next((i for i, v in enumerate(sentence)
                    if v[0].lower() == subject), None)
    data = {'subject': subject}
    for i in range(subject_idx, len(sentence)):
        found_action = False
        for j, (token, tag) in enumerate(sentence[i+1:]):
            if tag in VERBS:
                data['action'] = token
                found_action = True
            if tag in NOUNS and found_action == True:
                data['object'] = token
                data['phrase'] = sentence[i: i+j+2]
                return data
    return {}

def hyperize(token):
    word, tag = token
    S = []
    if tag == "NN":
        S = wn.synsets(word, pos=wn.NOUN)
    if tag == "RB":
        S = wn.synsets(word, pos=wn.ADV)
        S.extend(wn.synsets(word, pos=wn.ADJ))
    if tag == "JJ":
        S = wn.synsets(word, pos=wn.ADV)
        S.extend(wn.synsets(word, pos=wn.ADJ))
    if tag in ("VB", "VBG", "VBD"):
        S = wn.synsets(word, pos=wn.VERB)
    if not S:
        return set()
    H = {thing for s in S for thing in s.hypernyms()}
    if not H:
        H = S
    
    return {n for s in H for n in s.lemma_names()}

def hyped_tokens(tokens):
  return [hyperize(t) for t in trigram_tagger(tokens)]