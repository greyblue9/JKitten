import pythonrc
from pythonrc import *
from load_model import *


def tensor_data(p):
  data = (
    p.data
    if hasattr(p, "data")
    and any(c.__name__ == "Parameter" for c in type(p).__mro__)
    else p
  )
  import numpy as np

  dtype = getattr(np, str(p.data.dtype).split(".")[-1])
  return np.array(
    tuple(np.array(p.data[row], dtype=dtype) for row in range(p.data.shape[0])),
    dtype=dtype,
  )


import pickle

from pathlib import Path

pdir = Path("model") / "parameters"
pdir.mkdir(parents=True, exist_ok=True)
for idx, param in enumerate(model.parameters()):
  with open(pdir / f"{idx:03d}.pickle", "wb") as f:
    pickle.dump(f, param)
