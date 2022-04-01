import logging
logging.root.addHandler(logging.StreamHandler())
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
import asyncio
import sys
import threading
import time
from asyncio import get_event_loop_policy
from os import getenv
from threading import Thread, current_thread
import nextcord.utils
from dotenv import load_dotenv
from nextcord.ext.commands import Bot
from pathlib import Path
load_dotenv()

import hack_nextcord
from nextcord.gateway import DiscordWebSocket
import nextcord.gateway
from nextcord import utils
_orig_from_json = utils._from_json
_log_file = open("messages.jsonl", "a+", encoding="utf-8")

def _from_json_wrapped(jsonstr):
  obj = _orig_from_json(jsonstr)
  log.debug("Got object: %s", obj)
  _log_file.write(jsonstr)
  _log_file.write("\x0a")
  _log_file.flush()
  return obj
utils._from_json = _from_json_wrapped

bot = Bot(command_prefix=".")
def start_bot():
  token = (
    getenv("Token", getenv("DISCORD_BOT_TOKEN")).strip('"')
  )
  thread = current_thread()
  log.info(
    "Starting bot with token '%s%s%s' on thread: %s",
    token[0:5], "*" * len(token[5:-5]), token[-5:], thread
  )
  bot.run(token)

loop = get_event_loop_policy().new_event_loop()
t = Thread(target=start_bot, daemon=True)
t.start()
while True:
  pass