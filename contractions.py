#!/usr/bin/env python3

ucfirst = lambda i: i[:1].upper() + i[1:].lower()
import json, sys

path = "contractions.html"
import pythonrc
from pythonrc import *
from pathlib import Path
import re

f = Path(path)
text = f.read_text()
from bs4 import BeautifulSoup as BS

doc = BS(text)
doc = BS(doc.prettify())
lookup = [
  (
    re.sub(
      r"\b([a-z]+) [A-Z].*$",
      r"\1",
      re.sub(
        r"\s+",
        " ",
        r.select("td")[0].text.split("(")[0].split("/")[0],
        re.DOTALL,
      ),
    )
    .split("[")[0]
    .replace("\u2018", "'")
    .strip(),
    re.sub(
      r"\b([a-z]+) [A-Z].*$",
      r"\1",
      re.sub(
        r"\s+",
        " ",
        r.select("td")[1].text.split("(")[0].split("/")[0],
        re.DOTALL,
      ),
    )
    .split("[")[0]
    .replace("\u2018", "'")
    .strip(),
  )
  for r in doc.select("tr")
  if len(r.select("td")) == 2
]
lookup2 = lookup + [(k.replace("'", ""), v) for k, v in lookup]
data = {k.lower(): v.lower() for k, v in lookup2} | {k.upper(): v.upper() for k, v in lookup2} | {ucfirst(k): ucfirst(v) for k, v in lookup2}

Path("./bots/alice/maps/contractions.txt").write_text("\n".join(f"{k}:{v}" for k, v in data.items()))

Path("contractions.json").write_text(json.dumps(data, indent=2))
