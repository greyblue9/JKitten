#!/usr/bin/env python3

import pprint
from pathlib import Path
import sys

sys.path.insert(0, (Path.cwd() / "alice").as_posix())
import aiml.AimlParser


k = aiml.Kernel.Kernel()
if Path("brain.dmp").exists():
  k.bootstrap("brain.dmp", [])
else:
  k.bootstrap(
    None,
    list(
      map(Path.as_posix, Path("./").glob("**/*.aiml"))
    )
  )



