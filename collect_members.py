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
from pythonrc import get_package_modules, importAll
from dotenv import load_dotenv
from nextcord.ext.commands import Bot
from pathlib import Path

load_dotenv()
mods = importAll(get_package_modules("nextcord"))
import hack_nextcord
from nextcord.gateway import DiscordWebSocket
import nextcord.gateway
from nextcord import utils

_orig_from_json = utils._from_json
_log_file = open("messages.jsonl", "a+", encoding="utf-8")


def _from_json_wrapped(jsonstr):
  obj = _orig_from_json(jsonstr)
  # log.debug("Got object: %s", obj)
  _log_file.write(jsonstr)
  _log_file.write("\x0a")
  _log_file.flush()
  return obj


utils._from_json = _from_json_wrapped
"""
orig_recv_msg = DiscordWebSocket.received_message
async def received_message(self, msg, /):
  orig_msg = msg
  orig_buf = bytearray(self._buffer + b"")
  try:
    result = await orig_recv_msg(self, orig_msg)
    log.debug("Returning %s", result)
  finally:
    pass
  if type(orig_msg) is not bytes:
    return result
  
  buf = bytearray(self._buffe\r)
  buf.extend(orig_msg)
  try:
    log.debug("WS Received message: %s", buf)
  finally:
    return result
nextcord.gateway.DiscordWebSocket.received_message = received_message
"""


bot = Bot(command_prefix=".")


def start_bot():
  token = getenv("Token", getenv("DISCORD_BOT_TOKEN")).strip('"')
  thread = current_thread()
  log.info(
    "Starting bot with token '%s%s%s' on thread: %s",
    token[0:5],
    "*" * len(token[5:-5]),
    token[-5:],
    thread,
  )
  bot.run(token)


loop = get_event_loop_policy().new_event_loop()
t = Thread(target=start_bot, daemon=True)
t.start()

bots = {}
users = {}
messages = {}
guild_users = {}
user_guilds = {}
new_users = []
new_bots = []


def update_users():
  prev_users = dict(users)
  prev_bots = dict(bots)
  messages.update({m.id: m for g in bot.guilds for m in g._state._messages})
  users.update(
    {
      m.author.id: m.author
      for g in bot.guilds
      for m in list(g._state._messages)
      if not m.author.bot
    }
  )
  bots.update(
    {
      m.author.id: m.author
      for g in bot.guilds
      for m in list(g._state._messages)
      if m.author.bot
    }
  )
  new_users.clear()
  new_users.extend([users[uid] for uid in set(users) - set(prev_users)])
  new_bots.clear()
  new_bots.extend([bots[uid] for uid in set(bots) - set(prev_bots)])
  if print_new and (new_users or new_bots):
    log.info(
      "Added + %d -> %d bots, + %d -> %d users",
      len(new_bots),
      len(bots),
      len(new_users),
      len(users),
    )
  for u in new_users + new_bots:
    if hasattr(u, "guild"):
      guild_users.setdefault(u.guild.id, {})[u.id] = u
      user_guilds.setdefault(u.id, {})[u.guild.id] = u.guild
    if print_new:
      log.info(
        "Added uid=%s [%s#%s] in guild [%s] (@%s)",
        u.id,
        u.name,
        u.discriminator,
        u.guild.name if hasattr(u, "guild") else "?",
        u.top_role.name if hasattr(u, "top_role") else "?",
      )


def update_in_bg():
  while do_update:
    update_users()
    time.sleep(1)


do_update = True
print_new = True
t2 = Thread(target=update_in_bg, daemon=True)
t2.start()

import code
import readline
import rlcompleter

readline.parse_and_bind("tab: complete")
code.interact(locals())
