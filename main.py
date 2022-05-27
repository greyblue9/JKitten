import traceback
from bs4 import BeautifulSoup as BS
import inspect
import re
import asyncio
import inspect
import requests
import disnake
from disnake.ext import commands
from disnake.ext.commands import (
  AutoShardedBot,
  AutoShardedInteractionBot,
  Bot,
  Cog,
  CogMeta,
  Command,
  DefaultHelpCommand,
  GroupMixin,
  GuildContext,
  HelpCommand,
  InteractionBot,
  InvokableSlashCommand,
  ParamInfo,
  SubCommand,
  before_invoke,
  when_mentioned,
)
import json
import os, re
import logging

TEST_GUILDS = [
  936455318043504730,  # Kitten AI Testing
  846378738740232267,  # CUDA Server
  881146381891436565,  # The Chill Zone
  476190141161930753,  # Bot Test Python
]
logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(logging.StreamHandler())
log = logging.getLogger(__name__)
for log_name in (
  "disnake.__init__",
  "disnake.client",
  "disnake.gateway",
  "disnake.http",
  "disnake.opus",
  "disnake.player",
  "disnake.shard",
  "disnake.state",
  "disnake.voice_client",
  "disnake.webhook",
  "disnake.webhook",
  "watchdog.events",
  "watchdog.observers.fsevents",
  "watchdog.observers.fsevents2",
  "watchdog.observers.inotify_buffer",
):
  logging.getLogger(log_name).setLevel(logging.INFO)
from disnake.utils import find
from disnake.ui import Button, View
from disnake import *
from disnake.guild import Guild
from disnake.embeds import Embed
from disnake.user import Colour
from disnake.channel import TextChannel
from disnake.channel import TextChannel as Channel
import sys
from pathlib import Path
from bs4 import BeautifulSoup as BS # type:ignore
import traceback
from traceback import format_exc, format_exception, format_exception_only
import dotenv
from text_tools import repeated_sub, translate_urls, translate_emojis
import re
import asyncio, logging, threading, time
from asyncio import get_event_loop_policy
from os import getenv
from threading import Thread, current_thread
import disnake.utils
from dotenv import load_dotenv
from disnake.ext.commands import Bot
import requests
from aiohttp import ClientSession
import random
from disnake.client import *
from typing import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from importlib.machinery import all_suffixes
from functools import lru_cache
import nltk

load_dotenv()
DISCORD_BOT_TOKEN: str = getenv("Token", "")



def replace_mention(word, name_lookup):
  word = word.replace("!", "").replace("&", "").replace("@", "")
  if not word.startswith("<") or not word.endswith(">"):
    return word
  mbr_id = word[1:-1]
  if name := name_lookup.get(mbr_id):
    return name
  return word


class Class:
  @classmethod
  def forName(cls, name):
    from jnius import autoclass

    return autoclass(name)


name_lookup = {
  "863091076617601085": "Dekriel",
  "856229099952144464": "David",
  "955035045716979763": "Alice",
  "889338065020129310": "Mikko",
  '923229808803065907': 'Bob',
}
DEFAULT_UID = "0"
USE_JAVA = False

orig_cwd = Path.cwd()
k = chat = None
alice_bot = None

if USE_JAVA:
  from program_ab import *

  class AChat:
    def __init__(self, uid):
      self.uid = uid
      self.chat = None
    def multisentenceRespond(self, bot_message):
      global alice_bot
      if alice_bot is None:
        alice_bot = Class.forName("org.alicebot.ab.Bot")(
          "alice", orig_cwd.as_posix()
        )
      if self.chat is None:
        from __main__ import Main #type:ignore
        self.chat = Main.getOrCreateChat(alice_bot, True, self.uid)
      global chat
      chat = self.chat
      return self.chat.multisentenceRespond(bot_message)

else:
  
  class PChat:
    def __init__(self, uid):
      self.uid = uid
    def multisentenceRespond(self, bot_message):
      global k
      if k is None:
        sys.path.insert(0, (orig_cwd / "alice").as_posix())
        import aiml.Kernel
        k = alice_bot = aiml.Kernel.Kernel()
        print(k)
        if (orig_cwd / "brain.dmp").exists():
          k.bootstrap(orig_cwd / "brain.dmp", [])
        else:
          k.bootstrap(None, list(map(Path.as_posix, orig_cwd.glob("**/*.aiml"))))
      return k.respond(bot_message, self.uid)


async def get_chat(uid):
  if "PChat" in globals():
    return PChat(uid)
  return AChat(uid)


inputs = {}
responses = {}

PREFIX = "+" or "@Kitten"
intents = Intents.default()
intents.value |= disnake.Intents.messages.flag
intents.value |= getattr(disnake.Intents, "message_content").flag
intents.value |= disnake.Intents.guilds.flag
intents.value |= disnake.Intents.members.flag

bot = Bot(
  command_prefix=PREFIX,
  sync_commands=True,
  sync_commands_debug=True,
  sync_commands_on_cog_unload=True,
  test_guilds=[],
  # **options:
  status=Status.idle,
  intents=intents,
)


# function shared by all Cogs
def setup(bot: commands.Bot):
  module_name = [k for k in sys.modules.keys() if k.startswith("commands")][-1]
  class_name = module_name.split(".")[-1]
  module = sys.modules.get(module_name)
  cog_cls = getattr(module, class_name)
  cog_obj = cog_cls(bot)
  bot.add_cog(cog_obj)


if __name__ == "__main__":
  # Discover all the commands and load each one
  # into the bot
  dir: Path = Path("commands")
  for item in dir.iterdir():
    if item.name.endswith(".py"):
      name = f"{item.parent.name}.{item.stem}"
      log.info("Loading extension: %r", name)
      bot.load_extension(name)




_log = logging.getLogger(__name__)


def _cleanup_loop(loop):
  pass


def run(self, *args: Any, **kwargs: Any) -> None:
  loop = self.loop
  try:
    import signal
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
  except:
    pass

  async def runner():
    try:
      await self.start(*args, **kwargs)
    finally:
      if not self.is_closed():
        await self.close()

  def stop_loop_on_completion(f):
    loop.stop()

  future = asyncio.ensure_future(runner(), loop=loop)
  future.add_done_callback(stop_loop_on_completion)
  try:
    loop.run_forever()
  except KeyboardInterrupt:
    _log.info("Received signal to terminate bot and event loop.")
  finally:
    future.remove_done_callback(stop_loop_on_completion)
    _log.info("Cleaning up tasks.")
    _cleanup_loop(loop)
  if not future.cancelled():
    try:
      return future.result()
    except KeyboardInterrupt:
      # I am unsure why this gets raised here
      # but suppress it anyway
      return None


Client.run = run

k = None
@lru_cache
def get_kernel():
  global k
  if not k:
    sys.path.insert(0, (Path.cwd() / "alice").as_posix())
    import aiml.AimlParser, aiml.Kernel
    try:
      k = aiml.Kernel.Kernel()
    except (TypeError, ImportError):
      k = aiml.Kernel() # type: ignore
    log.info("Created python aiml Kernel: %s,", k)
    if Path("brain.dmp").exists():
      k.bootstrap("brain.dmp", [])
      log.info("Loaded brain into Kernel: %s,", k)
    else:
      k.bootstrap(None, list(map(Path.as_posix, Path("./").glob("**/*.aiml"))))
      k.saveBrain("brain.dmp")
    preds = {
      ln.split(":", 1)[0]: ln.split(":", 1)[1]
      for ln in
      (Path.cwd() / "bots"/ "alice"/"config" / "predicates.txt").read_text().splitlines()
      if len(ln.split(":")) >= 2
    }
    log.info("Loading %d predicates ...", len(preds))
    for pk, pv in preds.items():
      k.setBotPredicate(pk, pv)
  return k
get_kernel()

tagger = None
def pos_tag(sentence):
  global tagger
  import nltk
  if tagger is None:
    nltk.download(
     "averaged_perceptron_tagger")
    nltk.download("punkt")
    log.info("pos_tag: creating tagger")
    try:
      from nltk.corpus import treebank
    except Exception:
      log.info("pos_tag: nltk.download")
      nltk.download("treebank")
      from nltk.corpus import treebank
    from nltk.tag import PerceptronTagger
    log.info("pos_tag: PerceptronTagger()")
    tagger = PerceptronTagger()
    log.info("pos_tag: Train tagger")
    try:
      tagger.train(
       treebank.tagged_sents()[:500])
    except LookupError:
      nltk.download("treebank")
      tagger.train(
       treebank.tagged_sents()[:500])
    log.info("pos_tag: Got tagger: %s", tagger)
  tagged = tagger.tag(nltk.tokenize.word_tokenize(sentence))
  return tagged
pos_tag("")


class EvtHandler(FileSystemEventHandler):
  def on_any_event(self, evt):
    for fld, val in inspect.getmembers(evt):
      if not isinstance(val, str):
        continue
      if ".py" not in val: continue
      val2 = val.split("/")[-1]
      val2 = val2.split(".py")[0]
      val2 = val2.split(".")[-1]
      p = Path("commands") / f"{val2}.py"
      if not p.exists():
        continue
      name = ".".join([*p.parent.parts, p.stem])
      log.debug("%s: %s := %r", type(evt).__name__, fld, val2)
      try:
        bot.unload_extension(name)
      except Exception:
        pass
      if name in sys.modules:
        del sys.modules[name]
      bot.load_extension(name)
      log.info("Reloaded extension: %s", name)


def auto_reload_start(bot):
  evts = []
  obs = Observer()
  h = EvtHandler()
  obs.schedule(event_handler=h, path=Path.cwd() / "commands", recursive=True)
  obs.start()


def start_bot():
  thread = current_thread()
  log.info(
    "Starting bot with token '%s%s%s' on thread: %s",
    DISCORD_BOT_TOKEN[0:5],
    "*" * len(DISCORD_BOT_TOKEN[5:-5]),
    DISCORD_BOT_TOKEN[-5:],
    thread,
  )
  setattr(bot, "_rollout_all_guilds", True)
  auto_reload_start(bot)
  bot.run(DISCORD_BOT_TOKEN)


loop = get_event_loop_policy().get_event_loop()
loop.run_until_complete(get_chat(DEFAULT_UID))
Thread(target=start_bot).start()



def iter_over(coro):
  from threading import Event
  it = coro.__aiter__()
  rslts = []
  try:
    while True:
      f = asyncio.run_coroutine_threadsafe(
        it.__anext__(), loop
      )
      ev = Event()
      def on_done(_):
        ev.set()
      f.add_done_callback(on_done)
      if ev.wait():
        rslts.append(f.result())
      else:
        break
  except StopAsyncIteration:
    pass
  return rslts
  

import code
cons = code.InteractiveConsole(locals())
cons.push("import __main__")
cons.push("from __main__ import *")
cons.push("try: import pythonrc")
cons.push("except: pass")
cons.push("")
cons.push("import readline")
cons.push("import rlcompleter")
cons.push("readline.parse_and_bind('tab: complete')")
cons.interact(exitmsg="Goodbye!")
