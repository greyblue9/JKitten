import jnius_config
from typing import Any, Optional, Union
from collections.abc import Iterable
import subprocess
import sys
from os import getenv
from pathlib import Path
from zipfile import ZipFile
import logging
if sys.version_info[0:2] < (3, 9):
  from typing import Dict, Frozenset, List, Set, Tuple
else:
  Dict = dict
  Frozenset = frozenset
  List = list
  Set = set
  Tuple = tuple
log = logging.getLogger(__name__)


def get_classpath() -> List[Path]:
  JAR_DIR = Path(
    getenv("JAR_DIR", (Path.cwd()/"lib").as_posix())
  )
  classpath = [
    JAR_DIR / "Ab.jar",
    JAR_DIR / "deps.jar",
  ]
  for p in JAR_DIR.glob("jackson-*-2.13.1.jar"):
    classpath.append(p)
  for p in JAR_DIR.glob("jackson-*.jar"):
    if p in classpath:
      continue
    classpath.append(p)
  return classpath

def jmap_items_to_python(jmap) -> Iterable[Tuple[Any, Any]]:
  for e in jmap.entrySet():
    yield (e.getKey(), e.getValue())

def jmap_keys_to_python(jmap) -> Iterable[Any]:
  yield from jmap.keySet()

def jmap_values_to_python(jmap) -> Iterable[Any]:
  yield from jmap.values()


java_setup: Optional[Any] = None
def setup_jnius(classpath: List[Path]):
  global java_setup
  if java_setup is None:
    jnius_config.add_options(
      "-Xverify:none",
      "-Xmx3064m",
      "-Xrs"
    )
    log.debug("adding to classpath: %r", classpath)
    jnius_config.add_classpath(
      *
      tuple(
        map(Path.as_posix, classpath)
      )
    )
    
    for class_name in (
      "java.util.Map",
      "org.alicebot.ab.Nodemapper",
    ):
      log.debug("updating protocol map for %r", class_name)
      from jnius.reflect import protocol_map
      pmap = protocol_map.setdefault(class_name, {})
      pmap.update(
        items=jmap_items_to_python,
        keys=jmap_keys_to_python,
        values=jmap_values_to_python,
      )
      log.debug(
        "new protocol map for %r is: %r",
        class_name, pmap
      )
    log.debug("calling jnius.env.get_java_setup()")
    from jnius.env import get_java_setup
    java_setup = get_java_setup()
  log.debug("Returning java_setup: %r", java_setup)
  return java_setup


def java_classes_for_import(jarfile: Path) -> Dict[str, "jnius.JavaClass"]:
  log.debug(
    "collecting Java classes for import from %r", jarfile
  )
  from jnius import autoclass
  with (ZipFile(jarfile, "r")) as jar:
    classes_by_simple_name = {
      p.stem: autoclass(
        ".".join(
          p.parts[0:-1] + (p.stem,)
        )
      )
      for p in map(Path, jar.namelist())
      if p.suffix == ".class"
      and (
        p.stem == "Main"
        or (
          p.as_posix().startswith("org/alicebot/")
          and p.stem not in ("Path", "Bot")
        )
      )
    }
    log.debug(
      "returning name-JavaClass mapping for %d classes",
      len(classes_by_simple_name)
    )
    return classes_by_simple_name


classpath = get_classpath()
alice_jar = next(p for p in classpath if p.stem == "Ab")
java_setup = setup_jnius(classpath)
java_classes = java_classes_for_import(alice_jar)
globals().update(java_classes)

