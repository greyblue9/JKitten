#!/usr/bin/env python3

from pathlib import Path

exchgs = Path("data/sample.random_in.txt").read_text().split("\n\n")
import json

contractions = json.loads(Path("contractions.json").read_text())
exchgs = [e.upper().splitlines() for e in exchgs if len(e.splitlines()) == 2]
exchgs2 = [
  [
    " ".join([" ".join(contractions.get(w, w).split()) for w in ln.split()])
    .upper()
    .split(". ")[0]
    .split("?")[0]
    .split("! ")[0]
    for ln in excg
  ]
  for excg in exchgs
]
pronouns = json.loads(Path("pronouns.json").read_text())
flat_pronouns = {v.upper() for vals in pronouns.values() for v in vals}
from collections import Counter

ctr = Counter(
  [w for lns in exchgs2 for ln in lns for w in ln.split() if w not in flat_pronouns]
)
common = set(k for k, v in ctr.most_common()[0:3000])
exchgs_with_topic = [
  (
    (
      [
        w.replace(",", " , ")
        .replace("&", " AND ")
        .replace("<", " LESS THAN ")
        .replace(">", " GREATER THAN ")
        for w in exchg[0].replace(",", " , ").split()
        if w not in common and w.isalpha()
      ]
      or ["*"]
    )[0],
    exchg,
  )
  for exchg in exchgs2
]
print(
  "\n".join(
    [
      "0,{pattern},{that},{topic},{template},{filename}".format(
        pattern=h.replace(",", "#\\Comma"),
        that="*",
        topic=topic.replace(",", "\\#Comma"),
        template=r.replace(",", "\\#Comma"),
        filename="convos.aiml",
      )
      for topic, (h, r) in exchgs_with_topic
    ]
  )
)
