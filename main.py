import requests
import nextcord
from nextcord.ext import commands
import json
import os, re
import logging
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
import dotenv
import demoji
import re
USE_JAVA = True
EMOJI_REGEX = re.compile(
  ":([^: ][^:]*[^: ]):", 
  re.DOTALL | re.IGNORECASE
)
def translate_emojis(message: str) -> str:
  return EMOJI_REGEX.subn(
    " \\1 ",
    demoji.replace(
      message.split("]")[-1].strip("\n: ,")
    )
  )[0]

def translate_urls(message: str) -> str:
  prev = ""
  while message != prev:
    prev = message
    message = re.compile(
      "(https?://)([a-z]+)([^a-z ,;.]+)",
      re.DOTALL | re.IGNORECASE
    ).subn(
      "\\2 \\1",
      message
    )[0]
  message = re.compile(
    "\\s*(https?://)([^ ]*?)([, :;]|$)\\s*",
    re.DOTALL | re.IGNORECASE
  ).subn(
    ". ",
    message
  )[0]
  return message

orig_cwd = Path.cwd()
#sys.path.insert(0, "/data/media/0/src/sschatbot/src")
#sys.path.insert(1, "/data/media/0/src/sschatbot/src/bot")
#os.chdir("/data/media/0/src/sschatbot/src/bot")
if USE_JAVA:
  import jnius_config, subprocess, sys 
  jnius_config.add_options(
    "-Xverify:none", "-Xmx3064m", "-Xrs"
  )
  jnius_config.add_classpath(
    (orig_cwd / "lib" / "Ab.jar").as_posix(),
    (orig_cwd / "lib" / "deps.jar").as_posix(),
    (orig_cwd / "out").as_posix(),
  )
  import jnius
  jnius.reflect.protocol_map["java.util.Map"].update(
    items=lambda self: ((e.getKey(), e.getValue()) for e in self.entrySet()),
    keys=lambda self: self.keySet()
  )
  jnius.reflect.protocol_map.setdefault(
    "org.alicebot.ab.Nodemapper", {}
  ).update(
    items=lambda self: ((e.getKey(), e.getValue()) for e in self.entrySet()),
    keys=lambda self: self.keySet()
  )
  setup = jnius.env.get_java_setup()
  from zipfile import ZipFile
  with (
    ZipFile(orig_cwd / "lib" / "Ab.jar", "r")
  ) as jar:
    globals().update({
      Path(f).stem: jnius.autoclass(".".join(Path(f).parts[0:-1]+(Path(f).stem,)))
      for f in jar.namelist() 
      if Path(f).suffix == ".class" 
      and (
        f == "Main.class"
        or f.startswith("org/alicebot/")
      )
    })
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
    k.bootstrap(
      None,
      list(
        map(Path.as_posix, orig_cwd.glob("**/*.aiml"))
      )
    )
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
      'generated_responses': [],
      'past_user_inputs': inputs.get(uid),
      'text': message,
     }
     response = requests.post(
      API_URL, headers=headers, json=payload
     )
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
  or dotenv.get_key(
    dotenv_path=(orig_cwd / ".env"),
    key_to_get="DISCORD_BOT_TOKEN"
  )
  or dotenv.get_key(
    dotenv_path=(orig_cwd / ".env"),
    key_to_get="Token"
  )
  or eval("exec('raise Exception(\"Missing bot token.\")')")
)

PREFIX = "+" or "@Kitten"
intents = Intents.all()
bot = commands.Bot(
    command_prefix=PREFIX,
    help_command=None,
    status=Status.idle,
    intents=intents)


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
    ch = [
        c for c in guild.text_channels
        if c.permissions_for(guild.me).send_messages
    ][0]  # get first channel with speaking permissions
    print(ch)
    embed = nextcord.Embed(
        title=
        f"Thanks for Adding me to your server!\n\n I'm so glad to be in {guild.name}!\n \nTo talk with me, just have `@Kitten` in your message! \n \nTo setup a channel for me to talk in do:\n`+setup`",
        color=0x37393f)
    embed.set_author(name="Meow! I'm Kitten,")
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/attachments/889405771870257173/943436635343843328/cute_cat_4.jpeg"
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
    mbr = [m for m in mbrs if str(m.id) == str(mbr_id)][0]

    return mbr.name


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
async def setup(ctx: commands.Context, *, args=''):
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
        status = [(
            int(sk),
            ctx.guild.get_channel(int(sk)),
        ) for sk in (
            [config[str(guild.id)]] if str(guild.id) in config else [])]
        status_embed = Embed(title="Current Status",
                             color=0xff7575,
                             type='rich',
                             description='\n'.join([
                                 f"{ch.mention}: installed"
                                 for chid, ch in status
                             ]))
        if status:
            return ctx.reply(*args, embed=status_embed)
        return ctx.reply(*args)

    #
    if channel is None:
        await reply_maybe_embed(
            "Hello there! \n"
            " - To setup the AI on a channel, do `+setup #channel`. \n"
            " - To remove the AI from a channel, do `+setup remove #channel`.")
        return
    if not removing:
        if guild.id in config:
            await reply_maybe_embed(
                "Are you disabled?! You already have an AI channel set up!")
            return
        config[str(guild.id)] = channel.id
        save_config(config)
        await reply_maybe_embed(
            f"Alrighty! The channel {channel.mention} has been setup!")
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
            await reply_maybe_embed(
                f"The channel {channel.mention} is not set up.")
    else:
        await reply_maybe_embed(
            f"The channel {channel.mention} is not in your guild.")
    return


@bot.command(name="print-message-to-console")
async def print_message(ctx, message):
    print(message)
    await ctx.send("message printed in console")


async def guild(ctx):
    guild = ctx.guild
    return guild


@bot.listen()
async def on_message(message):
  response = ""
  channel_id = message.channel.id
  channel_name = translate_emojis(
    message.channel.name.split(
      b'\xff\xfe1\xfe'.decode("utf-16")
    )[-1].strip().strip("-")
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
  bot_message = re.compile(
    "([A-Za-z][a-z-]*)[_0-9-][^,.! ]*",
    re.DOTALL
  ).subn("\\1", bot_message)[0]
  print(
    f"[{message.author.name}][{message.guild.name}]:"
    f" {bot_message}"
  )
  for _ in range(1):
    if message.author.bot:
      print('message.author.bot')
      break
    if channel_name != "ai-chat-bot":
      print('channel_name != "ai-chat-bot"')
      return
    mention = f"<@!{bot.user.id}>"
    if bot.user == message.author:
      print('bot.user == message.author')
      break
    uid = message.author.name
    if (
      channel_name == "ai-chat-bot"
      or mention in message.content
    ):
        with message.channel.typing():
            if (
              len(bot_message.split()) == 1
              and re.search("lol|lmao|haha|hehe|ha ha|ahha", bot_message, re.IGNORECASE)
            ):
              break
            response = get_response(
              bot_message, message.author.name,
              model="microsoft/DialoGPT-large",
            )
            get_chat(uid).multisentenceRespond(
              response or "ok"
            )
            if not response or any(
              x.lower() in (response or "").lower()
              for x in (
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
                "Hey, I'm over here,"
              )
            ):
                print("Requesting a reply from second model")
                response = get_response(
                  bot_message, message.author.name,
                  model="microsoft/DialoGPT-small",
                )
            if not response or any(
              x.lower() in (response or "").lower()
              for x in (
                "what you mean",
                "like, I know",
                "I know, right",
                "Are you a girl",
                "I'm not sure if you're",
                " being serious or not",
                "I'm not sure if yo",
                "being serious or not.",
                "reference to the song",
                "I'm over hereactly",
                "Thanks for the trade",
                "Hey, I'm over here,"
              )
            ):
                get_chat(uid).multisentenceRespond(bot_message or response)
                response = get_chat(uid).multisentenceRespond(response or bot_message)
            if not response or any(
                  x.lower() in (response or "").lower()
                  for x in (
                    "what you mean",
                    "Are you a girl",
                    "like, I know",
                    "I know, right",
                    "reference to the song",
                    "I'm over hereactly",
                    "Thanks for the trade",
                    "Hey, I'm over here,"
                  )
            ):
            
                response = get_chat(uid).multisentenceRespond(bot_message)
            if not response or any(
                  x.lower() in (response or "").lower()
                  for x in (
                    "what you mean",
                    "Are you a girl",
                    "like, I know",
                    "I know, right",
                    "reference to the song",
                    "I'm over hereactly",
                    "Thanks for the trade",
                    "Hey, I'm over here,"
                  )
            ):
                print("Requesting a reply from Alice")
                
                response = get_chat(uid).multisentenceRespond(
                      random.choice(
                        re.findall(
                          "\\b([a-z]+)\\b",
                          Path("/data/media/0/src/chatbot/ItsPhant__Bot-chan/src/program-y/test/programytest/aiml_tests/train_tests/maps/familiarpronoun.txt").read_text()
                        )
                      ) + ", " + bot_message  + "!"
                )
            if not response or any(
                  x.lower() in (response or "").lower()
                  for x in (
                    "are you a man",
                    "Are you a girl",
                    "how old are you",
                    "where are you?",
                    "i'm glad you",
                    "reference to the song",
                    "I'm over hereactly",
                    "Thanks for the trade",
                    "Hey, I'm over here,"
                  )
            ):
                print("Requesting a reply from Alice, #2")
                response = get_response(
                  response, message.author.name,
                  model="microsoft/DialoGPT-large",
                )
                get_chat(uid).multisentenceRespond(
                  response or "ok"
                )
                response = get_chat(
                    uid
                ).multisentenceRespond(
                      "I said, " + (
                        bot_message.lower()
                        .replace("'s", "  is")
                        .replace("?", "")
                      )
                )
        if response:
            print("replying with: {}".format(response))
            await message.reply(response)
  await bot.process_commands(message)

get_chat("0")
bot.run(DISCORD_BOT_TOKEN)