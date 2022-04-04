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
  pass
import random


TEXT_CHANNELS_FILE = orig_cwd / "text_channels.json"
if not TEXT_CHANNELS_FILE.exists():
  TEXT_CHANNELS_FILE.write_text(json.dumps({}))
DISCORD_BOT_TOKEN = (
  os.getenv("DISCORD_BOT_TOKEN")
  or os.getenv("Token")
  or dotenv.get_key(dotenv_path=(orig_cwd / ".env"), key_to_get="DISCORD_BOT_TOKEN")
  or dotenv.get_key(dotenv_path=(orig_cwd / ".env"), key_to_get="Token")
  or eval("exec('raise Exception(\"Missing bot token.\")')")
)
PREFIX = "+" or "@Kitten"
intents = Intents.default()
intents.value |= nextcord.Intents.messages.flag
intents.value |= nextcord.Intents.guilds.flag
bot = commands.bot.Bot(
  command_prefix=PREFIX,
  status=Status.idle,
  intents=intents,
)
async def get_channel(message):
  with open(TEXT_CHANNELS_FILE, "r") as file:
    guild = json.load(file)
    key = str(message.guild.id)
    if key in guild:
      return guild[key]
    return None
@bot.event
async def on_ready():
  print("bot is online")
@bot.event
async def on_guild_join(guild):
  ch = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages][
    0
  ]  # get first channel with speaking permissions
  print(ch)
  embed = nextcord.Embed(
    title=f"Thanks for Adding me to your server!\n\n I'm so glad to be in {guild.name}!\n \nTo talk with me, just have `@Kitten` in your message! \n \nTo setup a channel for me to talk in do:\n`+setup`",
    color=0x37393F,
  )
  embed.set_author(name="Meow! I'm Kitten,")
  embed.set_thumbnail(
    url="https://cdn.discordapp.com/attachments/889405771870257173/943436635343843328/cute_cat_4.jpeg"
  )
  await ch.send(embed=embed)
def load_config():
  with open(TEXT_CHANNELS_FILE, "r") as file:
    guild = json.load(file)
  return guild
def save_config(conf):
  with open(TEXT_CHANNELS_FILE, "w") as file:
    json.dump(conf, file, indent=4)
@bot.command(name="ping")
async def ping(ctx: commands.Context):
  await ctx.send(f"the bot ping is currently: {round(bot.latency * 1000)}ms")
def replace_mention(word, name_lookup):
  word = word.replace("!", "").replace("&", "").replace("@", "")
  if not word.startswith("<") or not word.endswith(">"):
    return word
  mbr_id = word[1:-1]
  if name := name_lookup.get(mbr_id):
    return name
  return word
@bot.command(pass_context=True)
async def whoami(ctx):
  if ctx.message.author.server_permissions.administrator:
    msg = "You're an admin {0.author.mention}".format(ctx.message)
    await ctx.send(msg)
  else:
    msg = "You're an average joe {0.author.mention}".format(ctx.message)
    await ctx.send(msg)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx: commands.Context, *, args=""):
  channel: Channel = None
  removing: bool = False
  words = args.split()
  if words and words[0] == "remove":
    removing = True
    # drop first arg
    args = " ".join(words[1:])
  channel_match: re.Match = re.search(r"<#(?P<id>[0-9]+)>", args)
  if channel_match:
    guild_: Guild = ctx.guild
    channel = guild_.get_channel(int(channel_match.group("id")))
  guild: Guild = ctx.guild
  config = load_config()
  print(
    f"Setup command: {args=!r} {words=} {channel_match=} {channel=!r} {removing=!r}"
  )
  def reply_maybe_embed(*args):
    status = [
      (
        int(sk),
        ctx.guild.get_channel(int(sk)),
      )
      for sk in ([config[str(guild.id)]] if str(guild.id) in config else [])
    ]
    status_embed = Embed(
      title="Current Status",
      color=0xFF7575,
      type="rich",
      description="\n".join([f"{ch.mention}: installed" for chid, ch in status]),
    )
    if status:
      return ctx.reply(*args, embed=status_embed)
    return ctx.reply(*args)
  #
  if channel is None:
    await reply_maybe_embed(
      "Hello there! \n"
      " - To setup the AI on a channel, do `+setup #channel`. \n"
      " - To remove the AI from a channel, do `+setup remove #channel`."
    )
    return
  if not removing:
    if guild.id in config:
      await reply_maybe_embed(
        "Are you disabled?! You already have an AI channel set up!"
      )
      return
    config[str(guild.id)] = channel.id
    save_config(config)
    await reply_maybe_embed(
      f"Alrighty! The channel {channel.mention} has been setup!"
    )
    return
  # renoving
  if channel.guild.id == guild.id:
    if str(guild.id) in config:
      del config[str(guild.id)]
      save_config(config)
      await reply_maybe_embed(
        f"The channel {channel.mention} has been removed. I'll miss you! :("
      )
    else:
      await reply_maybe_embed(f"The channel {channel.mention} is not set up.")
  else:
    await reply_maybe_embed(f"The channel {channel.mention} is not in your guild.")
  return
@bot.command(name="print-message-to-console")
async def print_message(ctx, message):
  print(message)
  await ctx.send("message printed in console")
async def guild(ctx):
  guild = ctx.guild
  return guild
  


def setup(bot: commands.Bot):
    module_name = [
      k for k in sys.modules.keys()
      if k.startswith("commands")
    ][-1]
    class_name = module_name.split(".")[-1]
    module = sys.modules.get(module_name)
    cog_cls = getattr(module, class_name)
    cog_obj = cog_cls(bot)
    bot.add_cog(cog_obj)


for file in Path("commands").glob("*.py"):
  bot.load_extension(f"commands.{file.stem}")
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

def start_bot():
  token = (
    getenv("Token", getenv("DISCORD_BOT_TOKEN")).strip('"')
  )
  thread = current_thread()
  log.info(
    "Starting bot with token '%s%s%s' on thread: %s",
    token[0:5], "*" * len(token[5:-5]), token[-5:], thread
  )
  bot._rollout_all_guilds = True
  global cogs
  cogs = bot._BotBase__cogs
  from auto_reload import auto_reload_start
  auto_reload_start(bot)
  bot.run(token)

loop = get_event_loop_policy().get_event_loop()
Thread(target=start_bot).start()
get_chat(DEFAULT_UID)
import code
chat = asyncio.run(get_chat("856229099952144464"))
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