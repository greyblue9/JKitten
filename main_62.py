import traceback
from bs4 import BeautifulSoup as BS

import asyncio
import requests
import nextcord
from nextcord.ext import commands
import json
import os, re
import logging
logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(logging.StreamHandler())
log = logging.getLogger(__name__)
for log_name in ("nextcord.__init__", "nextcord.client", "nextcord.gateway", "nextcord.http", "nextcord.opus", "nextcord.player", "nextcord.shard", "nextcord.state", "nextcord.voice_client", "nextcord.webhook", "nextcord.webhook"):
  logging.getLogger(log_name).setLevel(logging.INFO)
from nextcord.utils import find
from nextcord.ui import Button, View
from nextcord import *
from nextcord.guild import Guild
from nextcord.embeds import Embed
from nextcord.user import Colour
from nextcord.channel import TextChannel
from nextcord.channel import TextChannel as Channel
import sys
from webserver import keep_alive
from pathlib import Path
from bs4 import BeautifulSoup as BS
import traceback
from traceback import format_exc, format_exception, format_exception_only
import dotenv
import demoji
import re

BLACKLIST = {
  "JSFAILED",
  "SRAIXFAILED",
  "Did you mean ",
  "the last of us",
  "a good song",
  "a guy making a video ",
  "is the guy who made the video",
  "making a video",
  "not sure what that means",
  "not sure what you're trying to say",
  "want to talk about unknown",
  "right? like, I know",
  "Are you a girl",
  "being serious or not.",
  "reference to the song",
  "I'm over hereactly",
  "Thanks for the trade",
  "reference to the song",
  "are you a man",
  "Are you a girl",
  "reference to the song",
  "I'm over hereactly",
  "not sure what",
  "I know, right?",
}
name_lookup = {
  "856229099952144464": "Dekriel",
  "856229099952144464": "David",
  "955035045716979763": "Alice",
  "889338065020129310": "Mikko",
}
DEFAULT_UID = "856229099952144464"
USE_JAVA = True
EMOJI_REGEX = re.compile(":([^: ][^:]*[^: ]):", re.DOTALL | re.IGNORECASE)


def translate_emojis(message: str) -> str:
  return EMOJI_REGEX.subn(
    " \\1 ", demoji.replace(message.split("]")[-1].strip("\n: ,"))
  )[0]


def translate_urls(message: str) -> str:
  prev = ""
  while message != prev:
    prev = message
    message = re.compile(
      "(https?://)([a-z]+)([^a-z ,;.]+)", re.DOTALL | re.IGNORECASE
    ).subn("\\2 \\1", message)[0]
  message = re.compile(
    "\\s*(https?://)([^ ]*?)([, :;]|$)\\s*", re.DOTALL | re.IGNORECASE
  ).subn(". ", message)[0]
  return message


orig_cwd = Path.cwd()
if USE_JAVA:
  import jnius_config, subprocess, sys

  jnius_config.add_options("-Xverify:none", "-Xmx3064m", "-Xrs")
  jnius_config.add_classpath(
    "./lib/Ab.jar",
    "./lib.deps.jar",
    *(
      "lib/Ab.jar:lib/deps.jar:lib/jackson-core-2.13.1.jar:lib/jackson-databind-2.13.1.jar".strip().split(
        ":"
      )
    ),
  )
  import jnius

  jnius.reflect.protocol_map["java.util.Map"].update(
    items=lambda self: ((e.getKey(), e.getValue()) for e in self.entrySet()),
    keys=lambda self: self.keySet(),
  )
  jnius.reflect.protocol_map.setdefault(
    "org.alicebot.ab.Nodemapper", {}
  ).update(
    items=lambda self: ((e.getKey(), e.getValue()) for e in self.entrySet()),
    keys=lambda self: self.keySet(),
  )
  setup = jnius.env.get_java_setup()
  from zipfile import ZipFile

  with (ZipFile(orig_cwd / "lib" / "Ab.jar", "r")) as jar:
    from pathlib import Path
    globals().update(
      {
        Path(f).stem: jnius.autoclass(
          ".".join(Path(f).parts[0:-1] + (Path(f).stem,))
        )
        for f in jar.namelist()
        if Path(f).suffix == ".class"
        and (f == "Main.class" or f.startswith("org/alicebot/"))
        and not f.endswith("Path.class")
      }
    )
  alice_bot = None

  async def get_chat(uid):
    global alice_bot
    if alice_bot is None:
      alice_bot \
        = jnius.autoclass("org.alicebot.ab.Bot")(
            "alice", orig_cwd.as_posix()
          )
    return Main.getOrCreateChat(alice_bot, True, uid)

else:
  sys.path.insert(0, (orig_cwd / "alice").as_posix())
  import aiml.Kernel
  k = aiml.Kernel.Kernel()
  print(k)
  if (orig_cwd / "brain.dmp").exists():
    k.bootstrap(orig_cwd / "brain.dmp", [])
  else:
    k.bootstrap(None, list(map(Path.as_posix, orig_cwd.glob("**/*.aiml"))))

  class Chat:
    def __init__(self, uid):
      self.uid = uid

    def multisentenceRespond(self, bot_message):
      return k.respond(bot_message, self.uid)

  async def get_chat(uid):
    return Chat(uid)


import requests

inputs = {}
responses = {}
from aiohttp import ClientSession

if "LOCAL" in os.environ:
  from converse import get_response as get_response_orig
  async def get_response(message, uid, model=None):
    return get_response_orig(message, uid, model)
  
else:
  async def get_response(message, uid, model=None):
    if model is None:
      model = random.choices(
        (
          "facebook/blenderbot-400M-distill",
          "microsoft/DialoGPT-large",
        ),
        weights=(
          10,
          90,
        )
      )[0]
    token = "jTOJnGIVFERTJqsFsUkAQZuyZVvdfzDxTeXSeSDORMTbrdrKaouEtTvPBIGVYcLDdkACpfeeSAQbUNBjFqKHkFdLvqmruoghVGNSxvfZjbfpVfGgzjYdtKZAqOItCmZY"
    headers = {"Authorization": f"Bearer api_{token}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
      "generated_responses": [],
      "past_user_inputs": inputs.get(uid),
      "text": message,
    }
    async with ClientSession() as session:
      async with session.post(
        API_URL, headers=headers, json=payload
      ) as response:
        data = await response.json()
        pprint(data)
        reply = data.get("generated_text")
        return reply


import random
