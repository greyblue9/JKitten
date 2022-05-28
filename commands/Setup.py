from __main__ import *
from disnake.ext.commands.interaction_bot_base import CommonBotBase
from disnake.ext.commands import Cog
from disnake.ext.commands import Command


async def get_channel(self, message):
  with open(TEXT_CHANNELS_FILE, "r") as file:
    guild = json.load(file)
    key = str(message.guild.id)
    if key in guild:
      return guild[key]
    return None


class Setup(Cog):
  bot: CommonBotBase
  event = Cog.listener()

  def __init__(self, bot):
    self.bot = bot
    super().__init__()

  @event
  async def on_ready(self):
    print("bot is online")

  @event
  async def on_guild_join(self, guild):
    ch = [
      c for c in guild.text_channels if c.permissions_for(guild.me).send_messages
    ][
      0
    ]  # get first channel with speaking permissions
    print(ch)
    embed = disnake.Embed(
      title=f"Thanks for Adding me to your server!\n\n I'm so glad to be in {guild.name}!\n \nTo talk with me, just have `@Kitten` in your message! \n \nTo setup a channel for me to talk in do:\n`+setup`",
      color=0x37393F,
    )
    embed.set_author(name="Meow! I'm Kitten,")
    embed.set_thumbnail(
      url="https://cdn.discordapp.com/attachments/889405771870257173/943436635343843328/cute_cat_4.jpeg"
    )
    await ch.send(embed=embed)

  def load_config(self):
    with open(TEXT_CHANNELS_FILE, "r") as file:
      guild = json.load(file)
    return guild

  def save_config(self, conf):
    with open(TEXT_CHANNELS_FILE, "w") as file:
      json.dump(conf, file, indent=4)

  @Command
  async def ping(self, ctx: commands.Context):
    await ctx.send(f"the bot ping is currently: {round(bot.latency * 1000)}ms")

  
  @Command
  async def kill(self, ctx: commands.Context, message=""):
    ip = requests.get("https://ip.me").text
    doit = not message or (message and message.strip() == ip.strip())
    if not doit:
      return
    await ctx.reply(f"OK, I'll go kill myself. My IP is: " + ip)
    try:
      raise SystemExit(0)
    finally:
      await ctx.send(f"OK, I'm dead.")
      os.kill(os.getpid(), 9)
  
  @Command
  async def whoami(self, ctx):
    if ctx.message.author.server_permissions.administrator:
      msg = "You're an admin {0.author.mention}".format(ctx.message)
      await ctx.send(msg)
    else:
      msg = "You're an average joe {0.author.mention}".format(ctx.message)
      await ctx.send(msg)

  @commands.has_permissions(administrator=True)
  @Command
  async def setup(self, ctx: commands.Context, *, args=""):
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
    config = self.load_config()
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
        description="\n".join(
          [f"{ch.mention}: installed" for chid, ch in status]
        ),
      )
      if status:
        return ctx.reply(*args, embed=status_embed)
      return ctx.reply(*args)

    #
    if channel is None:
      await reply_maybe_embed(
        "Hello there! \n "
        " - To setup the AI on a channel, do "
        "`+setup #channel`. \n "
        " - To remove the AI from a channel, "
        "do `+setup remove #channel`."
      )
      return
    if not removing:
      if guild.id in config:
        await reply_maybe_embed(
          "Are you disabled?! " "You already have an AI channel set up!"
        )
        return
      config[str(guild.id)] = channel.id
      self.save_config(config)
      await reply_maybe_embed(
        f"Alrighty! The channel " f"{channel.mention} has been setup!"
      )
      return
    # renoving
    if channel.guild.id == guild.id:
      if str(guild.id) in config:
        del config[str(guild.id)]
        self.save_config(config)
        await reply_maybe_embed(
          f"The channel {channel.mention} "
          f"has been removed. I'll miss you! :("
        )
      else:
        await reply_maybe_embed(f"The channel {channel.mention} is not set up.")
    else:
      await reply_maybe_embed(
        f"The channel {channel.mention} " f"is not in your guild."
      )
    return

  @Command
  async def print_message(self, ctx, message):
    print(message)
    await ctx.send("message printed in console")
