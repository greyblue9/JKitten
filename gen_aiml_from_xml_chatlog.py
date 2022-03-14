#!/usr/bin/env python3

import bs4, re, sys
import warnings
warnings.filterwarnings(action="ignore")

from bs4 import BeautifulSoup
from collections import namedtuple
Message = namedtuple("Message", ["time", "sender", "to", "text"])
from pythonrc import get_xml_from_string, readstring, writeFile
import nltk
nltk.download('averaged_perceptron_tagger')

names = set(readstring("bots/alice/sets/names.txt").upper().splitlines())
NAME_RE = re.compile("(?:^|(?<=>| ))({})(?=$| |[?:;!,+?])".format("|".join(re.escape(n) for n in names)), re.IGNORECASE)

doc = get_xml_from_string("<log>\n{}\n</log>".format(sys.stdin.read()))
msgnodes = doc.findall("./message")
from urllib.parse import unquote
parsed = []
for n in msgnodes:
  if not all(
    k in n.attrib for k in ("time", "from", "to", "text")
  ):
    continue
  try:
    text = BeautifulSoup(
        unquote(n.attrib.get("text"))
      )
    text = next(next(next(next(
      text.children
    ).children).children).children)
  except StopIteration:
    continue
  msg = Message(
    int(unquote(n.attrib.get("time"))),
    unquote(n.attrib.get("from")),
    unquote(n.attrib.get("to")),
    text,
  )
  if msg.text:
    parsed.append(msg)

reply_map = {}
aiml = BeautifulSoup("<aiml />")
aiml = aiml.select("aiml")[0]


for msg in parsed:
  # print(msg, file=sys.stderr)
  replies = sorted(
    (
      m for m in parsed 
      if m.to == msg.sender 
      and m.time >= msg.time
      and m.text
    ),
    key=lambda i: i.time
  )
  reply = replies[0] if replies else None
  if reply is None:
    continue
  inpt = msg.text.strip()
  inpt = inpt.replace("'", "")
  inpt = inpt.upper()
  inpt_parts = re.split("(?:(?<= )|^)[^a-zA-Z0-9'\" -]+(?= |$)", inpt)
  for inpt in inpt_parts:
    if "-" in inpt:
      continue
    if ":" in inpt:
      continue
    try:
      topic = sorted(
        [
          (k, v)
          for k, v in nltk.pos_tag(
            nltk.tokenize.wordpunct_tokenize(
              ", ".join(inpt_parts).upper() 
              + ". " 
              + reply.text.replace("'","").upper()
            )
          )
          if
          k.upper() not in ("LOL", "DOES", "DOESN", "SURE", "YEA", "YES", "YEP", "AH", "CAN", "ME", "I", "THE", "A")
          and (
            (k.upper() not in names
            or k.upper() in ("PAGE", "LINK", "WEB", "CANDY", "MAT", "CAT", "LACE", "POTTER", "TAG"))
            and set("HAE").difference(k)
            and set("HM").difference(k)
            and set("LO").difference(k)
            and set("LMAO").difference(k)
            and set("OMG").difference(k)
            and set("ROFL").difference(k)
            and set("COUZ").difference(k)
            and set("OK").difference(k)
          )
          and k[0].isalpha()
        ],
        key=lambda i: (
          (20 * (i[1] in ("NN", "N", "DO", "OO", "OP"))) 
          + (10 * (i[1] in ("VV", "V", "VP", "VB", "AV")))
          + (7 * (i[1] == "PRP"))
        ),
      )[-1][0].upper()
      if topic == "I": topic = "ME"
    except IndexError:
      continue
    inpt = re.sub(
      r"(?<=\W)((?:[A-Z][a-z]*)(?:[^a-zA-Z0-9]))+",
      "",
      inpt,
      re.DOTALL
    )
    inpt = re.sub(r"(^|(?<=\s))\S*[0-9-]\S*(?=$|\s)", "*", inpt)
    inpt = re.sub(r"(\w+)[^a-zA-Z0-9*_ ]+(\w*)", r"\1\2", inpt, re.DOTALL)
    resp = reply.text
    reply_map[inpt] = (resp, topic)
    sys.stderr.write(f"[{topic}]  {inpt} --> {resp}\x0A")
    
for key, (value,topic) in reply_map.items():
  cat = BeautifulSoup(
    "<category>" 
    "<pattern />"
    "<template>"
      "<think>"
        "<set name=\"topic\" />"
        "<set name=\"that\" />"
      "</think>"
      "<text />"
    "</template>"
    "</category>"
  )
  cat = cat.select("category")[0]
  patel = cat.select("pattern")[0]
  tmpel = cat.select("text")[0]
  topset1 = cat.select("set")[0]
  topset2 = cat.select("set")[1]
  tmpel.string = value
  wds = key.split()
  
  if len(wds) > 6:
    wdsnew = wds[0:3] + ["_"] + wds[-3:]
    key = " ".join(wds)
  topset1.string = topset2.string = topic.upper()
  
  patel.string = key.upper()
  pat_esc = str(patel)
  tmp_esc = str(tmpel)
  tmpel_new = BeautifulSoup(tmp_esc)
  tmpel_new = tmpel_new.select("text")[0]
  tmpel.replace_with(tmpel_new)
  
  patel_new = BeautifulSoup(NAME_RE.sub("*", pat_esc))
  patel_new = patel_new.select("pattern")[0]
  patel.replace_with(patel_new)
  tmpel_new.replace_with_children()
  
  aiml.append(cat)
                                                      
print("<?xml version=\"1.0\"?>")
print(aiml.prettify())