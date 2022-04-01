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
  
  
tagger = None 
import nltk
def pos_tag(sentence):
  global tagger 
  if tagger is None:
    nltk.download('treebank')
    from nltk.corpus import treebank
    from nltk.tag import PerceptronTagger
    tagger = PerceptronTagger()
    tagger.train(treebank.tagged_sents()[:300])
  tagged = tagger.tag(
    nltk.tokenize.word_tokenize(sentence)
  )
  return tagged
from tagger import *
async def wolfram_alpha(inpt, uid):
  log.info("wolfram_alpha(%r, %r) query", inpt, uid)
  from bs4 import BeautifulSoup as BSimport
  import urllib.parse, urllib.request
  API_URL = (f"http://api.wolframalpha.com/v2/query?"
             f"appid=2U987T-JJR9G73T6P"
             f"&input={urllib.parse.quote(inpt)}")
  response = ""
  async with ClientSession() as session:
    async with session.get(
      API_URL
    ) as resp:
      doc = BS(await resp.read(), features="lxml")
      print(doc)
      for ans in sorted(
          filter(
            lambda i: i.text,
            doc.select(
              'pod[error=false] > subpod[title=""] > plaintext'
            ),
          ),
          key=lambda i: len(i.text),
      ):
        if " is " in str(ans.text):
          response = str(ans.text)
          response = response.split("...")[0]
          if ". " in response:
            response = response.rsplit(".", 1)[0]
            response += "."
          log.info("wolfram_alpha(%r, %r) returning %r",
            inpt, uid, response)
          return response
        if "|" in str(ans.text) or "(" in str(ans.text):
          continue
      if response:
        log.info("wolfram_alpha(%r, %r) returning %r",
          inpt, uid, response)
        return response
      for ans in doc.select(
        "subpod plaintext"
      ):
        if "|" in str(ans.text):
          continue
        response = str(ans.text)
        log.info("wolfram_alpha(%r, %r) #2 returning %r",
          inpt, uid, response)
        return response
      log.debug(doc.prettify())
  log.info("wolfram_alpha(%r, %r) returning empty",
          inpt, uid, response)
  return ""
from pprint import pprint
async def gpt_response(bot_message, uid=DEFAULT_UID):
  log.debug("gpt_response(%r, %r)", bot_message, uid)
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  response = await get_response(bot_message, uid)
  if not response:
    return ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      log.debug("gpt_response(%r, %r) discarding response %r due to blacklist", bot_message, uid, response)
      return ""
  if "" in set(
    filter(
      None,
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input or "", last_response or "", bot_message or "")
      )
    )
  ):
    log.debug("gpt_response(%r, %r) discarding response %r because it repeats a previous entry", bot_message, uid, response)
    return ""
  log.info("query GPT for %r returns %r", 
      bot_message, response)
  return response
async def google(bot_message, uid=DEFAULT_UID):
  log.debug("google(%r, %r) called", bot_message, uid)
  chat = await get_chat(uid)
  cats = categorize(bot_message.lower())
  topic = "*"
  if cats["entities"]:
    topic = cats["entities"][0]
  response = (
    jnius.autoclass("org.alicebot.ab.Sraix")
      .sraixPannous(bot_message, topic, chat)
  )
  if "SRAIXFAILED" in response:
    log.debug("google(%r, %r) failed with %r", bot_message, uid, response)
    return ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      log.debug("google(%r, %r) discarding response %r because it repeats a previous entry", bot_message, uid, response)
      return ""
  log.info("query Google for %r returns %r", 
      bot_message, response)
  return response
async def alice_response(bot_message, uid):
  log.debug("alice_response(%r, %r)", bot_message, uid)
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  global loop
  chat = await get_chat(uid)
  cats = await loop.run_in_executor(
    None, categorize, bot_message.lower()
  )
  topic = "*"
  if cats["entities"]:
    log.debug("alice_response(%r, %r) setting topic to %r", bot_message, uid, topic)
    topic = cats["entities"][0]
    chat.predicates.put("topic", topic)
  log.debug("alice_response(%r, %r): query %r", bot_message, uid, bot_message)
  response = await loop.run_in_executor(
    None, chat.multisentenceRespond, bot_message
  )
  log.debug("alice_response(%r, %r): result: %r", bot_message, uid, response)
  
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      log.debug("alice_response(%r, %r) discarding response %r due to blacklist", bot_message, uid, response)
      return ""
  if "" in set(
    filter(
      None,
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input, last_response, bot_message)
      )
    )
  ):
    log.debug("alice_response(%r, %r) discarding response %r because it repeats a previous entry", bot_message, uid, response)
    return ""
  
  log.info(  
    "alice_response query for %r returns %r", 
    bot_message, response
  )
  return response
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
  bot.run(token)
loop = get_event_loop_policy().get_event_loop()
start_bot()
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
