import traceback
from bs4 import BeautifulSoup as BS

(
  
  
    
  
chat.multisentenceRespond(last_input)
  
  
  
  
  )
  
  
  
  
    
    
  
(
await loop.run_in_executor(None, sleep, delay)
  
  if "" in set(
    filter(
      None,
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input, last_response, bot_message)
      )
    )
  if "" in set(
    filter(
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input, last_response, bot_message)
      )
  
  
  if "" in set(
    filter(
      None,
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input, last_response, bot_message)
      )
    )
  
)
  
        
  
        
(
  "The Game",
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
def replace_mention(word, members):
  if not word.startswith("<@"):
    return word
  word = word.replace("!", "")
  mbr_id = int(word[2:-1])
  mbrs = [b for g in bot.guilds for b in g.members]
  mbrx = [m for m in mbrs if str(m.id) == str(mbr_id)]
  if mbrx:
    return mbrx[0].name
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
def wolfram_alpha(inpt):
  from bs4 import BeautifulSoup as BSimport
  import urllib.parse, urllib.request
  resp = urllib.request.urlopen(
    urllib.request.Request(
      f"http://api.wolframalpha.com/v2/query?"
      f"appid=2U987T-JJR9G73T6P"
      f"&input={urllib.parse.quote(inpt)}"
    )
  )
  doc = BS(resp.read().decode())
  for ans in sorted(
      filter(
        lambda i: i.text,
        doc.select(
          'pod[error=false] > subpod[title=""] > plaintext'
        ),
      ),
      key=lambda i: len(i.text),
  ):
    response = str(ans.text)
    return response
  return ""
  
from pprint import pprint
def gpt_response(bot_message, uid="0"):
  response = get_response(
    bot_message, uid, model="microsoft/DialoGPT-large",
  )
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      return ""
  log.info("query GPT for %r returns %r", 
      bot_message, response)
  return response
def google(bot_message, uid="0"):
  chat = get_chat(uid)
  cats = categorize(bot_message.lower())
  topic = "*"
  if cats["entities"]:
    topic = cats["entities"][0]
  
  response = (
    jnius.autoclass("org.alicebot.ab.Sraix")
      .sraixPannous(bot_message, topic, chat)
  )
  if "SRAIXFAILED" in response:
    return ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      return ""
  log.info("query Google for %r returns %r", 
      bot_message, response)
  return response
def alice_response(bot_message, uid):
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  chat = get_chat(uid)
  chat.multisentenceRespond(last_input)
  chat.multisentenceRespond(last_response)
  response = chat.multisentenceRespond(bot_message)
  if any(b.lower() in response.lower() for b in BLACKLIST):
    return ""
  if re.subn(
    or "[^a-z]+", "", response.lower(), re.IGNORECASE
  )[0] in set(
    filter(
      None,
      re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
      for s in (last_input, last_response, bot_message)
    )
  ):
    return ""
  log.info(  
    "query Alice for %r returns %r", 
    bot_message, response
  )
  return response
@bot.listen()
async def on_message(message):
  response = ""
  channel_id = message.channel.id
  channel_name = translate_emojis(
    message.channel.name.split(b"\xff\xfe1\xfe".decode("utf-16"))[-1]
    .strip()
    .strip("-")
  ).strip("-")
  print(f"channel_id = {channel_id}")
  print(f"channel_name = {channel_name}")
  print(f"{message.channel=}")
  print(f"{message.author=}")
  print(f"{message.guild=}")
  bot_message = " ".join(
    (
      replace_mention(word, message.guild.members)
      for word in message.content.split()
    )
  )
  bot_message = translate_emojis(bot_message)
  bot_message = translate_urls(bot_message)
  bot_message = re.compile("([A-Za-z][a-z-]*)[_0-9-][^,.! ]*", re.DOTALL).subn(
    "\\1", bot_message
  )[0]
  print(f"[{message.author.name}][{message.guild.name}]:" f" {bot_message}")
  plan = []
  uid = message.author.name
  mention = f"<@!{bot.user.id}>"
  if message.author.bot:
    return
  if channel_name != "ai-chat-bot":
    return
  if bot.user == message.author:
    return
  if (
    channel_name != "ai-chat-bot" 
    and mention not in message.content
  ):
    return
  def respond(new_response):
    nonlocal response
    response = new_response
    log.info(
      "Responding to %r with %r", bot_message, response
    )
    inputs.setdefault(uid, []).append(bot_message)
    responses.setdefault(uid, []).append(response)
    return message.reply(response)
  
  try:
    with message.channel.typing():
      cats: dict = categorize(bot_message.lower())
      # {
      #   "tagged": tagged, "items": items,
      #   "question": question, "person": person,
      #   "entities": tuple(entities),
      #   "attributes": tuple(attributes),
      #   "clauses": tuple(clauses),
      # {
      pprint(cats)
      by_pos = { pos:wd for wd,pos in cats["tagged"] }
      pronouns_pos = {
        pos for pos,m in tag_meanings.items() 
        if "pro" in str(m).lower()
      }
      personal_pos = {
        pos for pos,m in tag_meanings.items() 
        if "pers" in str(m).lower()
      }
      has_pronouns = pronouns_pos.intersection(by_pos)
      has_personal = personal_pos.intersection(by_pos)
      has_proper_noun = "NN" in (
        pos for word, pos in pos_tag(bot_message)
      )
      
      if (
        "age" in cats["attributes"] and cats["entities"]
        or "how many " in bot_message.lower()
        or "how long " in bot_message.lower()
        or "how much " in bot_message.lower()
        or "how old " in bot_message.lower()
        or "'s age" in bot_message.lower()
      ):
        if new_response := wolfram_alpha(bot_message):
          return respond(new_response)
      if has_personal and "name" in cats["attributes"]:
        if new_response := alice_response(bot_message):
          return respond(new_response)
      
      exclaim_score = sum(
        1
        for pos in
        dict(cats["tagged"]).values()
        if pos in ("DT", "JJR", "PRP",)
      )
      if exclaim_score >= 3:
        if new_response := gpt_response(bot_message, uid):
          return respond(new_response)
      
      if m := re.compile(
        "^(?:do you know |what is |what'?s |"
        "^ *)([0-9]+.*[0-9])[,?.]* *$",
        re.DOTALL | re.IGNORECASE,
      ).search(bot_message):
          try:
            return respond(
              m.group(1) + " is " +
              str(eval(m.group(1).strip())) + "."
            ) 
          except:
            pass
      
      if not response:
        if (not cats["question"]
          or (not cats["person"] and not cats["entities"])
        ):
           if new_response := gpt_response(bot_message, uid):
             response = new_response
        
        elif new_response := wolfram_alpha(bot_message, uid):
          return respond(new_response)
        
        elif new_response := google(bot_message, uid):
          return respond(new_response)
      
      if response.endswith(", seeker."):
         response = response.removesuffix(", seeker.") + "."
      if (
          "hiya" == response.lower().strip()
          or "i am dad" in response.lower()
          or "i'm dad" in response.lower()
          or "hi jon" in response.lower()
          or ", jon" in response.lower()
          or "hi kyle" in response.lower()
          or ", kyle" in response.lower()
          or "hi paul" in response.lower()
          or ", paul" in response.lower()
          or "hi mat" in response.lower()
          or ", mat" in response.lower()
        ):
          response = random.choice(
            [
              f"Hey there! How are you, {message.author.mention}?",
              "Hello",
              "Hi what'a up?",
              f"Hey, good to see you again, {message.author.mention}.",
              f"Welcome back, {message.author.mention}!",
              f"Yo what's up, {message.author.mention}",
              "Hi, it's good to see you again.",
              "Hello there." "Well, hello!",
              "Hiya bro",
              f"Yay {message.author.mention}! You're exactly who I was hoping to see.",
              "Sup, dude?",
            ]
          )
  except Exception as exc:
    exc_str = "" "\n%s" % (
      "\x0a".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    )
    embed = Embed(
      description=(
        rf"Oops! I had some trouble responding to your message. \x0a"
        rf"```py\x0a{exc_str}```"
      ),
      title="Alice Python Error",
      color=Color.red(),
    )
    embed.add_field(name="Your name", value=message.author.name)
    embed.add_field(name="Your message", value=message.content)
    embed.add_field(name="Translated message", value=bot_message)
    await message.reply(
      response,
      embed=embed,
    )
  else:
    if response:
      return respond(response)
  finally:
    await bot.process_commands(message)
get_chat("0")
bot.run(DISCORD_BOT_TOKEN)
import requests
import nextcord
from nextcord.ext import commands
import json
import os, re
import logging
logging.root.setLevel(logging.INFO)
logging.root.addHandler(logging.StreamHandler())
log = logging.getLogger(__name__)
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
  "he means",
  "The Game",
  "the last of us",
  "What is this",
  "a good song",
  "a guy making a video ",
  "is the guy who made the video",
  "is the guy who made the video",
  "making a video",
  "not sure what that means",
  "not sure what you're trying to say",
  "want to talk about unknown",
  "what you mean",
  "like, I know",
  "I know, right",
  "I'm not sure if you're",
  "Are you a girl",
  " being serious or not",
  "I'm not sure if yo",
  "being serious or not.",
  "reference to the song",
  "I'm over hereactly",
  "Thanks for the trade",
  "Hey, I'm over here",
  "what you mean",
  "Are you a girl",
  "What you mean",
  "like, I know",
  "I know, right",
  "reference to the song",
  "I'm over hereactly",
  "Thanks for the trade",
  "Hey, I'm over here,",
  "are you a man",
  "Are you a girl",
  "how old are you",
  "where are you?",
  "i'm glad you",
  "reference to the song",
  "I'm over hereactly",
  "Thanks for the trade",
  "Hey, I'm over here,",
}
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
  def get_chat(uid):
    global alice_bot
    if alice_bot is None:
      alice_bot = Bot("alice", orig_cwd.as_posix())
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
  def get_chat(uid):
    return Chat(uid)
import requests
inputs = {}
responses = {}
if "LOCAL" in os.environ:
  from converse import get_response
else:
  def get_response(message, uid, model="microsoft/DialoGPT-large"):
    token = "jTOJnGIVFERTJqsFsUkAQZuyZVvdfzDxTeXSeSDORMTbrdrKaouEtTvPBIGVYcLDdkACpfeeSAQbUNBjFqKHkFdLvqmruoghVGNSxvfZjbfpVfGgzjYdtKZAqOItCmZY"
    headers = {"Authorization": f"Bearer api_{token}"}
    inputs.setdefault(uid, []).append(message)
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
      "generated_responses": [],
      "past_user_inputs": inputs.get(uid),
      "text": message,
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    reply = data.get("generated_text")
    responses.setdefault(uid, []).append(reply)
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
bot = commands.bot.AutoShardedBot(
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
def replace_mention(word, members):
  if not word.startswith("<@"):
    return word
  word = word.replace("!", "")
  mbr_id = int(word[2:-1])
  mbrs = [b for g in bot.guilds for b in g.members]
  mbrx = [m for m in mbrs if str(m.id) == str(mbr_id)]
  if mbrx:
    return mbrx[0].name
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
def wolfram_alpha(inpt):
  from bs4 import BeautifulSoup as BSimport
  import urllib.parse, urllib.request
  resp = urllib.request.urlopen(
    urllib.request.Request(
      f"http://api.wolframalpha.com/v2/query?"
      f"appid=2U987T-JJR9G73T6P"
      f"&input={urllib.parse.quote(inpt)}"
    )
  )
  doc = BS(resp.read().decode())
  for ans in sorted(
      filter(
        lambda i: i.text,
        doc.select(
          'pod[error=false] > subpod[title=""] > plaintext'
        ),
      ),
      key=lambda i: len(i.text),
  ):
    response = str(ans.text)
    return response
  return ""
  
from pprint import pprint
def gpt_response(bot_message, uid="0"):
  response = get_response(
    bot_message, uid, model="microsoft/DialoGPT-large",
  )
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      return ""
  log.info("query GPT for %r returns %r", 
      bot_message, response)
  return response
def google(bot_message, uid="0"):
  chat = get_chat(uid)
  cats = categorize(bot_message.lower())
  topic = "*"
  if cats["entities"]:
    topic = cats["entities"][0]
  
  response = (
    jnius.autoclass("org.alicebot.ab.Sraix")
      .sraixPannous(bot_message, topic, chat)
  )
  if "SRAIXFAILED" in response:
    return ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      return ""
  log.info("query Google for %r returns %r", 
      bot_message, response)
  return response
def alice_response(bot_message, uid):
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  chat = get_chat(uid)
  chat.multisentenceRespond(last_input)
  chat.multisentenceRespond(last_response)
  response = chat.multisentenceRespond(bot_message)
  if any(b.lower() in response.lower() for b in BLACKLIST):
    return ""
  if re.subn(
    or "[^a-z]+", "", response.lower(), re.IGNORECASE
  )[0] in set(
    filter(
      None,
      re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
      for s in (last_input, last_response, bot_message)
    )
  ):
    return ""
  log.info(  
    "query Alice for %r returns %r", 
    bot_message, response
  )
  return response
@bot.listen()
async def on_message(message):
  response = ""
  channel_id = message.channel.id
  channel_name = translate_emojis(
    message.channel.name.split(b"\xff\xfe1\xfe".decode("utf-16"))[-1]
    .strip()
    .strip("-")
  ).strip("-")
  print(f"channel_id = {channel_id}")
  print(f"channel_name = {channel_name}")
  print(f"{message.channel=}")
  print(f"{message.author=}")
  print(f"{message.guild=}")
  bot_message = " ".join(
    (
      replace_mention(word, message.guild.members)
      for word in message.content.split()
    )
  )
  bot_message = translate_emojis(bot_message)
  bot_message = translate_urls(bot_message)
  bot_message = re.compile("([A-Za-z][a-z-]*)[_0-9-][^,.! ]*", re.DOTALL).subn(
    "\\1", bot_message
  )[0]
  print(f"[{message.author.name}][{message.guild.name}]:" f" {bot_message}")
  plan = []
  uid = message.author.name
  mention = f"<@!{bot.user.id}>"
  if message.author.bot:
    return
  if channel_name != "ai-chat-bot":
    return
  if bot.user == message.author:
    return
  if (
    channel_name != "ai-chat-bot" 
    and mention not in message.content
  ):
    return
  def respond(new_response):
    nonlocal response
    response = new_response
    log.info(
      "Responding to %r with %r", bot_message, response
    )
    inputs.setdefault(uid, []).append(bot_message)
    responses.setdefault(uid, []).append(response)
    return message.reply(response)
  
  try:
    with message.channel.typing():
      cats: dict = categorize(bot_message.lower())
      # {
      #   "tagged": tagged, "items": items,
      #   "question": question, "person": person,
      #   "entities": tuple(entities),
      #   "attributes": tuple(attributes),
      #   "clauses": tuple(clauses),
      # {
      pprint(cats)
      by_pos = { pos:wd for wd,pos in cats["tagged"] }
      pronouns_pos = {
        pos for pos,m in tag_meanings.items() 
        if "pro" in str(m).lower()
      }
      personal_pos = {
        pos for pos,m in tag_meanings.items() 
        if "pers" in str(m).lower()
      }
      has_pronouns = pronouns_pos.intersection(by_pos)
      has_personal = personal_pos.intersection(by_pos)
      has_proper_noun = "NN" in (
        pos for word, pos in pos_tag(bot_message)
      )
      
      if (
        "age" in cats["attributes"] and cats["entities"]
        or "how many " in bot_message.lower()
        or "how long " in bot_message.lower()
        or "how much " in bot_message.lower()
        or "how old " in bot_message.lower()
        or "'s age" in bot_message.lower()
      ):
        if new_response := wolfram_alpha(bot_message):
          return await respond(new_response)
      if has_personal and "name" in cats["attributes"]:
        if new_response := alice_response(bot_message):
          return await respond(new_response)
      
      exclaim_score = sum(
        1
        for pos in
        dict(cats["tagged"]).values()
        if pos in ("DT", "JJR", "PRP",)
      )
      if exclaim_score >= 3:
        if new_response := gpt_response(bot_message, uid):
          return await respond(new_response)
      
      if m := re.compile(
        "^(?:do you know |what is |what'?s |"
        "^ *)([0-9]+.*[0-9])[,?.]* *$",
        re.DOTALL | re.IGNORECASE,
      ).search(bot_message):
          try:
            return await respond(
              m.group(1) + " is " +
              str(eval(m.group(1).strip())) + "."
            ) 
          except:
            pass
      
      if not response:
        if (not cats["question"]
          or (not cats["person"] and not cats["entities"])
        ):
           if new_response := gpt_response(bot_message, uid):
             response = new_response
        
        elif new_response := wolfram_alpha(bot_message, uid):
          return await respond(new_response)
        
        elif new_response := google(bot_message, uid):
          return await respond(new_response)
      
      if response.endswith(", seeker."):
         response = response.removesuffix(", seeker.") + "."
      if (
          "hiya" == response.lower().strip()
          or "i am dad" in response.lower()
          or "i'm dad" in response.lower()
          or "hi jon" in response.lower()
          or ", jon" in response.lower()
          or "hi kyle" in response.lower()
          or ", kyle" in response.lower()
          or "hi paul" in response.lower()
          or ", paul" in response.lower()
          or "hi mat" in response.lower()
          or ", mat" in response.lower()
        ):
          response = random.choice(
            [
              f"Hey there! How are you, {message.author.mention}?",
              "Hello",
              "Hi what'a up?",
              f"Hey, good to see you again, {message.author.mention}.",
              f"Welcome back, {message.author.mention}!",
              f"Yo what's up, {message.author.mention}",
              "Hi, it's good to see you again.",
              "Hello there." "Well, hello!",
              "Hiya bro",
              f"Yay {message.author.mention}! You're exactly who I was hoping to see.",
              "Sup, dude?",
            ]
          )
  except Exception as exc:
    exc_str = "" "\n%s" % (
      "\x0a".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    )
    embed = Embed(
      description=(
        rf"Oops! I had some trouble responding to your message. \x0a"
        rf"```py\x0a{exc_str}```"
      ),
      title="Alice Python Error",
      color=Color.red(),
    )
    embed.add_field(name="Your name", value=message.author.name)
    embed.add_field(name="Your message", value=message.content)
    embed.add_field(name="Translated message", value=bot_message)
    await message.reply(
      response,
      embed=embed,
    )
  else:
    if response:
      return await respond(response)
  finally:
    await bot.process_commands(message)
get_chat("0")
bot.run(DISCORD_BOT_TOKEN)
  
    
      print("replying with: {}".format(response))
      inputs.setdefault(uid, []).append(bot_message)
      responses.setdefault(uid, []).append(response)
      await message.reply(response)
return respond(new_response)
      
          
          return respond(new_response)
          
          
    
          
  
)
(
log.info("query WA returns %r", response)
          inputs.setdefault(uid, []).append(bot_message)
          responses.setdefault(uid, []).append(response)
          await message.reply(response)
          
          
     
             
           if new_response:
             
           
      
    
             
(
new_response)
if new_response := 
return respond(new_response)
return respond(new_response)
      if m:
        

