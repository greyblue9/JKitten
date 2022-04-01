import traceback
from bs4 import BeautifulSoup as BS

(
          
)
  
            
  
  
  
  
  
  
            
(
)
  
            
            
            
            
  
   
             
{
(
(
          
(
)
)
)
(
  
          
  
          
)
  
          
  [('what', 'WP'),
            ('is', 'VBZ'),
            ('your', 'PRP$'),
            ('name', 'NN'),
            (',', ','),
            ('alice', 'NN')]}
values()
(
'PRP$'
          
          
          
)
(
(
(
)
(
)
(
)
(
)
(
         
          
(
{'attributes': (),
 'clauses': (),
 'entities': ('alice',),
 'items': ['alice', 'alice'],
      channel_name != "ai-chat-bot" 
      and mention not in message.content
      and f"<@{self.bot.user.id}>" not in message.content
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
          if new_response := await alice_response(bot_message):
            return await respond(new_response)
        
        exclaim_score = sum(
          1
          for pos in
          dict(cats["tagged"]).values()
          if pos in ("DT", "JJR", "PRP",)
        )
        if exclaim_score >= 3:
          if new_response := await gpt_response(bot_message, uid):
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
             if new_response := await gpt_response(bot_message, uid):
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
          f"Oops! I had some trouble responding to your message. \x0a"
          f"```py\x0a{exc_str}```"
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
      await self.bot.process_commands(message)
from __main__ import *
class Chat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    super().__init__()
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
    uid = str(message.author.id)
    username = message.author.name
    if m := re.search(
      "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
      username,
      re.DOTALL
    ):
      realname = m.group("name").lower().capitalize()
    name_lookup[str(message.author.id)] = realname
    name_lookup[str(message.author.username)] = realname
    bot_message = " ".join(
      (
        replace_mention(word, name_lookup)
        for word in message.content.split()
      )
    )
    bot_message = translate_emojis(bot_message)
    bot_message = translate_urls(bot_message)
    
    log.info(
      f"[{message.author.name}][{message.guild.name}]:"
      f" {bot_message}"
    )
    mention = f"<@!{bot.user.id}>"
    if message.author.bot:
      return
    if bot.user == message.author:
      return
    if (
      channel_name != "ai-chat-bot" 
      and mention not in message.content
      and f"<@{bot.user.id}>" not in message.content
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
          if new_response := await alice_response(bot_message):
            return await respond(new_response)
        
        exclaim_score = sum(
          1
          for pos in
          dict(cats["tagged"]).values()
          if pos in ("DT", "JJR", "PRP",)
        )
        if exclaim_score >= 3:
          if new_response := await gpt_response(bot_message, uid):
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
             if new_response := await gpt_response(bot_message, uid):
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
          f"Oops! I had some trouble responding to your message. \x0a"
          f"```py\x0a{exc_str}```"
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
from __main__ import *
class Chat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    super().__init__()
  @self.bot.listen()
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
    uid = str(message.author.id)
    username = message.author.name
    if m := re.search(
      "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
      username,
      re.DOTALL
    ):
      realname = m.group("name").lower().capitalize()
    name_lookup[str(message.author.id)] = realname
    name_lookup[str(message.author.username)] = realname
    bot_message = " ".join(
      (
        replace_mention(word, name_lookup)
        for word in message.content.split()
      )
    )
    bot_message = translate_emojis(bot_message)
    bot_message = translate_urls(bot_message)
    
    log.info(
      f"[{message.author.name}][{message.guild.name}]:"
      f" {bot_message}"
    )
    mention = f"<@!{self.bot.user.id}>"
    if message.author.bot:
      return
    if self.bot.user == message.author:
      return
    if (
      channel_name != "ai-chat-bot" 
      and mention not in message.content
      and f"<@{self.bot.user.id}>" not in message.content
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
          if new_response := await alice_response(bot_message):
            return await respond(new_response)
        
        exclaim_score = sum(
          1
          for pos in
          dict(cats["tagged"]).values()
          if pos in ("DT", "JJR", "PRP",)
        )
        if exclaim_score >= 3:
          if new_response := await gpt_response(bot_message, uid):
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
             if new_response := await gpt_response(bot_message, uid):
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
          f"Oops! I had some trouble responding to your message. \x0a"
          f"```py\x0a{exc_str}```"
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
      await self.bot.process_commands(message)
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
  
  
    
    
  
  
      
      
      
    
    
def setup()  
def setup(bot: commands.Bot):
    module_name = [k for k in sys.modules.keys() if k.startswith("commands")][-1]
    class_name = module_name.split(".")[-1]
    module = sys.modules.get(module_name)
    cog_cls = getattr(module, class_name)
    cog_obj = cog_cls(bot)
    bot.add_cog(cog_obj)
)
(
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
)
(
)
(
    
    
)
(
  
)
(
f"<@!{bot.user.id}>"
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
  uid = str(message.author.id)
  username = message.author.name
  if m := re.search(
    "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
    username,
    re.DOTALL
  ):
    realname = m.group("name").lower().capitalize()
  name_lookup[str(message.author.id)] = realname
  name_lookup[str(message.author.username)] = realname
  bot_message = " ".join(
    (
      replace_mention(word, name_lookup)
      for word in message.content.split()
    )
  )
  bot_message = translate_emojis(bot_message)
  bot_message = translate_urls(bot_message)
  
  log.info(
    f"[{message.author.name}][{message.guild.name}]:"
    f" {bot_message}"
  )
  mention = f"<@!{bot.user.id}>"
  if message.author.bot:
    return
  if bot.user == message.author:
    return
  if (
    channel_name != "ai-chat-bot" 
    and mention not in message.content
    and f"<@{bot.user.id}>" not in message.content
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
        if new_response := await alice_response(bot_message):
          return await respond(new_response)
      
      exclaim_score = sum(
        1
        for pos in
        dict(cats["tagged"]).values()
        if pos in ("DT", "JJR", "PRP",)
      )
      if exclaim_score >= 3:
        if new_response := await gpt_response(bot_message, uid):
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
           if new_response := await gpt_response(bot_message, uid):
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
        f"Oops! I had some trouble responding to your message. \x0a"
        f"```py\x0a{exc_str}```"
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
f"<@!{bot.user.id}>"
from __main__ import *
class Chat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    super().__init__()
  @commands.Cog.listener()
  async def on_message(self, message):
    response = ""
    channel_id = message.channel.id
    channel_name = translate_emojis(
      message.channel.name.split(b"\xff\xfe1\xfe".decode("utf-16"))[-1]
      .strip()
      .strip("-")
    ).strip("-")
    print(f"channel_id = {channel_id}")
    print(f"channel_name = {channel_name}")
    uid = str(message.author.id)
    username = message.author.name
    if m := re.search(
      "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
      username,
      re.DOTALL
    ):
      realname = m.group("name").lower().capitalize()
    name_lookup[str(message.author.id)] = realname
    name_lookup[str(message.author.name)] = realname
    bot_message = " ".join(
      (
        replace_mention(word, name_lookup)
        for word in message.content.split()
      )
    )
    bot_message = translate_emojis(bot_message)
    bot_message = translate_urls(bot_message)
    
    log.info(
      f"[{message.author.name}][{message.guild.name}]:"
      f" {bot_message}"
    )
    mention = f"<@!{self.bot.user.id}>"
    #if message.author.bot:
    #  return
    if self.bot.user == message.author:
      return
    if (
      channel_name != "ai-chat-bot" 
      and mention not in message.content
      and f"<@{self.bot.user.id}>" not in message.content
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
      if message.author.bot:
        response = f"<@{message.author.id}> {response}"
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
          (
            cats['attributes'] == () or
            set(cats['attributes']).intersection({
              'name', 'age', 'favorite',
              'master', 'botmaster', 'creator', 'inventor',
              'boss', 'friend', 'buddy', 'pal', 'nemesis',
              'birthday', 'job', 'occupation'
            })
          )
          and cats['clauses'] == ()
          and cats['entities'] in ((), ('alice',),)
          and set(cats['items']) in (set(), {'alice'})
          and cats['person'] == False
          and cats['question'] == True
          and 'PRP$' in dict(cats['tagged']).values()
        ):
          if new_response := await alice_response(bot_message, uid):
            return await respond(new_response)
        
        if (
          "age" in cats["attributes"] and cats["entities"]
          or "how many " in bot_message.lower()
          or "how long " in bot_message.lower()
          or "how much " in bot_message.lower()
          or "how old " in bot_message.lower()
          or "'s age" in bot_message.lower()
          or re.search("^what is [^ ]+($|,|\\.)", bot_message.lower())
        ):
          if new_response := await wolfram_alpha(bot_message, uid):
            return await respond(new_response)
  
        if has_personal and "name" in cats["attributes"]:
          if new_response := await alice_response(bot_message):
            return await respond(new_response)
        
        exclaim_score = sum(
          1
          for pos in
          dict(cats["tagged"]).values()
          if pos in ("DT", "JJR", "PRP",)
        )
        if exclaim_score >= 3:
          if new_response := await gpt_response(bot_message, uid):
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
             if new_response := await gpt_response(bot_message, uid):
               response = new_response
          
          elif new_response := await wolfram_alpha(bot_message, uid):
            return await respond(new_response)
          
          elif new_response := await google(bot_message, uid):
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
          f"Oops! I had some trouble responding to your message. \x0a"
          f"```py\x0a{exc_str}```"
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
      await self.bot.process_commands(message)

