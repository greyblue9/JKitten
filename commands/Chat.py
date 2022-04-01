from __main__ import *

async def alice_response(bot_message, uid):
  log.debug("alice_response(%r, %r)", bot_message, uid)
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  if "what is your name" in last_response.lower():
    name = bot_message.strip(".? !").split()[-1]
    name_lookup[uid] = name
    return random.choice([
      f"It's great to meet you, {name}.",
      f"Well! How do you do, {name}?",
      f"Gosh, I've been waiting so long and now I'm finally speaking with *the* {name}!",
    ])
  import gc
  import asyncio.unix_events
  loop = [o for o in gc.get_objects() if isinstance(o, asyncio.unix_events._UnixSelectorEventLoop) and o.is_running][0]
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

  if "your name is dekriel" in response.lower():
    name = name_lookup.get(uid)
    if name:
      response = f"Your name is {name}."
    else:
      response = "I don't know your name. What is your name?"
  
  if "Hari" in response:
    response = re.sub("\\bHari\\b", "Alice", response)
  
  log.info(
    "alice_response query for %r returns %r",
    bot_message, response
  )
  return response

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
    if uid not in name_lookup:
      realname = message.author.name
      if m := re.search(
        "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
        realname, re.DOTALL
      ):
        realname = m.group("name").lower().capitalize()
      name_lookup[uid] = realname
    
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
        has_poss_pronoun = "PRP" in (
          pos for word, pos in pos_tag(bot_message)
        )
        
        if (
          bot_message.lower().startswith("my name is ")
        ):
          name = bot_message.strip(".!? ").split()[-1]
          name_lookup[uid] = name
          name_lookup[message.author.name] = name
          inputs.setdefault(uid, []).append("What is your name?")
          if new_response := await alice_response(bot_message, uid):
            return await respond(new_response)
        
        if (
          (
            cats['attributes'] == () or
            set(cats['attributes']).intersection({
              'name', 'age', 'favorite',
              'master', 'botmaster', 'creator', 'inventor',
              'boss', 'friend', 'buddy', 'pal', 'nemesis',
              'birthday', 'job', 'occupation'
            })
            or (has_poss_pronoun 
              and bot_message.split()[0] in ("what", "how"))
          )
          and cats['entities'] in ((), ('alice',),)
          and cats['question'] == True
          and (has_poss_pronoun or 
               'PRP$' in dict(cats['tagged']).values())
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
          if new_response := await alice_response(bot_message, uid):
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