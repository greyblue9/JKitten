#!/usr/bin/env python3

import sys; path ="pronouns.html"; from pathlib import Path; f = Path(path); text = f.read_text(); from bs4 import BeautifulSoup as BS; doc = BS(text); sec = doc.select("section")[0]; import itertools, json; print(json.dumps(dict([("".join(h.text.split(". ")[1:]).split(" / ")[0].split(" Pronouns")[0].strip().lower() or "all", [n.text.split("(")[0].strip() for n in itertools.chain(h.next_sibling.select("li"), h.next_sibling.next_sibling.select("li"))]) for h in sec.select("h2")[1:]]), indent=2))
import json; from pathlib import Path; pdata = json.loads(Path("pronouns.json").read_text()); Path("./bots/alice/config/pronouns.txt").write_text("\n".join(sorted({v for vals in pdata.values() for v in vals})));
for cat, vals in pdata.items():
  (Path("./bots/alice/sets") / f"{cat}.txt").write_text("\n".join(sorted(vals)))
  (Path("./bots/alice/sets") / f"pronouns_{cat}.txt").write_text("\n".join(sorted(vals)))
