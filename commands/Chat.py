from __main__ import *
from disnake.ext.commands.interaction_bot_base import CommonBotBase
from disnake.ext.commands import Cog
from disnake.ext.commands import Command
from pprint import pprint
from tagger import *
import nltk
import aiohttp


CHANNEL_NAME_WHITELIST = {
  "open-chat",
  "global-chat",
  "🤖︱ai-chat-bot",
  "general",
  "alice-bot",
  "speichren",
}


class Class:
  @classmethod
  def forName(cls, name):
    from jnius import autoclass

    return autoclass(name)


BLACKLIST = {
  "JSFAILED",
  "I know, right",
  "serious or not",
  "I'm not sure what you're trying to say",
  "joking or not",
  "SRAIXFAILED",
  "the last of us",
  "a guy making a video ",
  "is the guy who made the video",
  "making a video",
  "want to talk about unknown",
  "Are you a girl",
  "reference to the song",
  "I'm over hereactly",
  "Thanks for the trade",
  "being sarcastic",
  "reference to the song",
  "Are you a girl",
  "reference to the song",
  "I'm over hereactly",
  "not sure what you mean",
  "web search",
  "good song",
  "search the web",
  "<oob>",
}


tagger = None


def pos_tag(sentence):
  global tagger
  if tagger is None:
    nltk.download("treebank")
    from nltk.corpus import treebank
    from nltk.tag import PerceptronTagger

    tagger = PerceptronTagger()
    tagger.train(treebank.tagged_sents()[:300])
  tagged = tagger.tag(nltk.tokenize.word_tokenize(sentence))
  return tagged


async def wolfram_alpha(inpt, uid=None):
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  log.info("wolfram_alpha(%r, %r) query", inpt, uid)
  from bs4 import BeautifulSoup as BSimport
  import urllib.parse, urllib.request

  API_URL = (
    f"http://api.wolframalpha.com/v2/query?"
    f"appid=2U987T-JJR9G73T6P"
    f"&input={urllib.parse.quote(inpt)}"
  )
  response = ""
  async with ClientSession() as session:
    async with session.get(API_URL) as resp:
      doc = BS(await resp.read())
      print(doc)
      for ans in reversed(doc.select("subpod > img + plaintext")):
        if ans.text:
          return str(ans.text)
      for ans in sorted(
        filter(
          lambda i: i.text,
          doc.select('pod[error=false] > subpod[title=""] > plaintext'),
        ),
        key=lambda i: len(i.text),
      ):
        if " is " in str(ans.text):
          response = str(ans.text)
          response = response.split("...")[0]
          if ". " in response:
            response = response.rsplit(".", 1)[0]
            response += "."
          log.info("wolfram_alpha(%r, %r) returning %r", inpt, uid, response)
          return response
        if "|" in str(ans.text) or "(" in str(ans.text):
          continue
      if response:
        log.info("wolfram_alpha(%r, %r) returning %r", inpt, uid, response)
        return response
      for ans in doc.select("subpod plaintext"):
        if "|" in str(ans.text):
          continue
        response = str(ans.text)
        log.info("wolfram_alpha(%r, %r) #2 returning %r", inpt, uid, response)
        return response
      log.debug(doc.prettify())
  log.info("wolfram_alpha(%r, %r) returning empty", inpt, uid, response)
  return ""


async def get_response(message, uid, model=None):
  response = None
  inpt = bot_message = message
  data = {}
  for attempt in range(1):
    if response:
      return response
    if model is None:
      model = random.choices(
        model_names := (
          "microsoft/DialoGPT-large",
          "facebook/blenderbot-3B",
          "microsoft/DialoGPT-small",
        ),
        weights := (65, 25, 15),
      )[0]
    model_idx = model_names.index(model)
    weight = weights[model_idx]
    log.info(
      "\nget_response(%r, %r): selected model\n\n" "    %r   (weight: %s)\n\n",
      message,
      uid,
      model,
      weight,
    )
    token = "jTOJnGIVFERTJqsFsUkAQZuyZVvdfzDxTeXSeSDORMTbrdrKaouEtTvPBIGVYcLDdkACpfeeSAQbUNBjFqKHkFdLvqmruoghVGNSxvfZjbfpVfGgzjYdtKZAqOItCmZY"
    headers = {"Authorization": f"Bearer api_{token}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
      "generated_responses": [],
      "past_user_inputs": inputs.get(uid),
      "text": message,
    }
    async with ClientSession() as session:
      async with session.post(API_URL, headers=headers, json=payload) as response:
        try:
          data = await response.json()
        except aiohttp.client_exceptions.ContentTypeError:
          print(response.content)
          try:
            data = await response.json(content_type="application/json")
          except Exception as e:
            print(e)
        else:
          pprint(data)
        if not data:
          data = {"error": "No reply", "estimated_time": 5}
        if data.get("error"):
          await asyncio.sleep(data.get("estimated_time", 20))
          async with ClientSession() as session:
            async with session.post(
              API_URL, headers=headers, json=payload
            ) as response:
              try:
                data = await response.json(
                  content_type="application/json"
                )
              except Exception as e:
                print(e)
        if data:
          pprint(data)
        reply = data.get("generated_text")
        response = reply
        if not response:
          model = None
          continue
        for b in BLACKLIST:
          if b.lower() in response.lower() or response.lower() in b:
            log.debug(
              "get_response(%r, %r) discarding response %r due to blacklist",
              inpt,
              uid,
              response,
            )
            response = ""
            model = None
            break
        if not response:
          continue

        if (
          re.subn("[^a-z]+", "", response.lower(), re.IGNORECASE)[0]
          == re.subn("[^a-z]+", "", inpt.lower(), re.IGNORECASE)[0]
        ):
          log.debug(
            "get_response(%r, %r) discarding response %r because it repeats a previous entry",
            inpt,
            uid,
            response,
          )
          response = ""
          model = None
          continue
        return response
    return "wtf"


async def gpt_response(bot_message, uid=None):
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  log.debug("gpt_response(%r, %r)", bot_message, uid)
  last_input = inputs.setdefault(uid, [""])[-1]
  last_response = responses.setdefault(uid, [""])[-1]
  response = await get_response(bot_message, uid)
  if not response:
    return ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      log.debug(
        "gpt_response(%r, %r) discarding response %r due to blacklist",
        bot_message,
        uid,
        response,
      )
      return ""
  if "" in set(
    filter(
      None,
      (
        re.subn("[^a-z]+", "", s.lower(), re.IGNORECASE)[0]
        for s in (last_input or "", last_response or "", bot_message or "")
      ),
    )
  ):
    log.debug(
      "gpt_response(%r, %r) discarding response %r because it repeats a previous entry",
      bot_message,
      uid,
      response,
    )
    return ""
  log.info("query GPT for %r returns %r", bot_message, response)
  return response


async def google(bot_message, uid=None):
  return ""


import functools

strip_xtra = (
  lambda s: re.subn(
    "([a-z])'[a-z]*",
    "\\1",
    re.subn("(?<=[^a-zA-Z])'((?:[^'.]+|(?<=[a-z])'[a-z]*)+)(\\.?)'", "\\1", s)[0],
  )[0]
  .strip()
  .lower()
)


def find(coll, r):
  return (
    [coll[idx + 1 :] + coll[idx : idx + 1] for idx, w in enumerate(coll) if w in r][
      0
    ]
    if any(w in coll for w in r)
    else [coll]
  )


def google2(bot_message, uid=0, req_url=None):

  ans_marker = " ".join(
    find(
      re.subn("[.?!\t\n ]*$", "", bot_message.lower())[0].split(),
      ("is", "are," "were", "was"),
    )
  )

  query = '"{}"'.format(ans_marker)

  from bs4 import BeautifulSoup
  from pathlib import Path
  from urllib.request import Request, urlopen
  from urllib.parse import quote_plus

  if not req_url:
    req_url = "https://www.google.com/search?client=safari&rls=en&gbv=1&q={}&hl=en&num=10".format(
      quote_plus(query)
    )

  headers = {
    "Accept-Language": "en-us",
    "Host": "www.google.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
  }

  request = urlopen(Request(req_url, headers=headers))
  html = request.read()
  request.close()

  doc = BeautifulSoup(html)
  doc2 = doc
  [
    (e.clear() or e.replace_with_children()) if e else None
    for e in reversed(list(doc2.select("svg, script, style, link, meta, :empty")))
  ]
  [
    (e.replace_with_children()) if e else None
    for e in reversed(list(doc2.select("html, body, head, header, footer, form")))
  ]
  [
    ((a := pg.parent.parent).clear() or a.replace_with_children())
    if pg and pg.parent and pg.parent.parent
    else None
    for pg in doc2.select('a[href*="policies.google.com"]')
  ]
  [
    ((p := ac.parent.parent.parent).clear() or p.replace_with_children())
    if ac and ac.parent and ac.parent.parent and ac.parent.parent.parent
    else None
    for ac in doc2.select("accordion-entry-search-icon")
  ]
  descrips = [
    "\n".join(x.text for x in e.select("* > * > * > *"))
    for e in doc2.select(
      "div:first-child:last-child > div > div > div > div > div:first-child:last-child"
    )
  ]
  answers = list({
    #e.text[
    #  strip_xtra(e.text).index(
    #    strip_xtra(ans_marker)
    #  ) :
    #]
    e.text
    .strip(". ")
    .split(". ")[0]
    for e in doc.select("*")
    if strip_xtra(ans_marker) in strip_xtra(e.text)
  })
  for i, a in reversed(list(enumerate(answers))):
    if "Google Search" in a:
      print("popping answer", i, a)
      answers.pop(i)
  
  a_sorted = sorted([
    (
        (
             a.startswith("The ")
          or a.startswith("An ") 
          or a.startswith("An ") 
          or a.startswith("Mr. ") 
          or a.startswith("Ms. ") 
          or a.startswith("Mrs. ") 
          or a.startswith("Miss ") 
          or a.startswith("Dr. ")
        ) * 10 
      + (a[0].isupper() * 100) 
      + (a[1].islower() * 60)
      + a.strip().endswith(".") * 70
      + (a[1].isupper() * -30)
      + (75 < len(a) < 500) * 50,
      + min((len(a) - 150) * 10, 100),
      a
    )
    for i, a in enumerate(answers)
  ])
  
  
  print(f"google2: a_sorted")
  pprint(a_sorted)
  answers = [a for score, a in reversed(a_sorted)]
  
  print(f"google2: answers")
  pprint(answers)
  next_url = None
  for elem in doc.select('a[aria-label="Next page"]'):
      next_url = elem.attrs.get("href")
      print(f"google2: next page is {next_url!r}")
  
  if answers:
    for answer in answers:
      print(f"google2: returning first answer: {answer=}")
      return answer
  elif next_url and not req_url:
    print(f"google2: trying next page")
    if answer := google2(bot_message, uid, next_url):
      print(f"google2: got answer from next page: {answer=}")
      return answer
  print(f"google2: fall back to google for {bot_message=}")
  return google(bot_message)


async def alice_response(bot_message, uid):
  return ""


class Chat(Cog):
  bot: CommonBotBase
  event = Cog.listener()

  def __init__(self, bot):
    self.bot = bot
    super().__init__()

  @Command
  async def wa(self, ctx, *, message):
    response = await wolfram_alpha(message)
    return await ctx.send(response)

  @Command
  async def google(self, ctx, *, message):
    response = await google(message)
    return await ctx.send(response)

  @Command
  async def alice(self, ctx, *, message):
    response = await alice_response(message, str(ctx.message.author.id))
    return await ctx.send(response)

  @event
  async def on_message(self, message):
    response = ""
    if "Focused Technophiles" not in message.guild.name:
      return
    if message.content.startswith("+"):
      await self.bot.process_commands(message)
      return
    channel_id = message.channel.id
    channel = message.channel
    in_whitelist = any(
      channel.name.lower() in f.lower() for f in CHANNEL_NAME_WHITELIST
    )
    uid = str(message.author.id)
    if uid not in name_lookup:
      realname = message.author.name
      if m := re.search(
        "^[^A-Za-z]*(?P<name>[a-zA-Z][a-z-]+[a-z])([^a-z].*|)$",
        realname,
        re.DOTALL,
      ):
        realname = m.group("name").lower().capitalize()
      name_lookup[uid] = realname

    bot_message = " ".join(
      (replace_mention(word, name_lookup) for word in message.content.split())
    )

    bot_message = translate_emojis(bot_message)
    if "https://" in bot_message or "http://" in bot_message:
      bot_message = translate_urls(bot_message)
    
    mention = f"<@!{self.bot.user.id}>"
    if self.bot.user == message.author:
      return
    ok = (
      in_whitelist
      or mention in message.content
      or "alice" in message.content.lower()
      or "alice " in bot_message.lower()
    )
    if not ok:
      return
    log.info(f"[{message.author.name}][{message.guild.name}]:" f" {bot_message}")
    def respond(new_response):
      nonlocal response
      response = new_response
      log.info("Responding to %r with %r", bot_message, response)
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
        by_pos = {pos: wd for wd, pos in cats["tagged"]}
        pronouns_pos = {
          pos for pos, m in tag_meanings.items() if "pro" in str(m).lower()
        }
        personal_pos = {
          pos for pos, m in tag_meanings.items() if "pers" in str(m).lower()
        }
        has_pronouns = pronouns_pos.intersection(by_pos)
        has_personal = personal_pos.intersection(by_pos)
        has_proper_noun = "NP" in (
          pos[0:2] for word, pos in pos_tag(bot_message)
        )
        has_poss_pronoun = "PRP" in (
          pos[0:3] for word, pos in pos_tag(bot_message)
        )
        print(f"{by_pos=}")
        print(f"{pronouns_pos=}")
        print(f"{personal_pos=}")
        print(f"{has_personal=}")
        print(f"{has_proper_noun=}")
        print(f"{has_poss_pronoun=}")
        if (
          cats["tagged"]
          and cats["tagged"][0]
          and cats["tagged"][0][0] in ("what", "who", "when", "where")
          and len(cats["tagged"]) > 1
          and cats["tagged"][1]
          and cats["tagged"][1][0] in ("is", "are")
          and cats["question"]
          and not cats["person"]
        ):
          print("Google")
          if new_response := google2(bot_message, uid):
            return await respond(new_response)

        if bot_message.lower().startswith("my name is "):
          name = bot_message.strip(".!? ").split()[-1]
          name_lookup[uid] = name
          name_lookup[message.author.name] = name
          inputs.setdefault(uid, []).append("What is your name?")
          if new_response := await alice_response(bot_message, uid):
            return await respond(new_response)

        if (
          (
            cats["attributes"] == ()
            or set(cats["attributes"]).intersection(
              {
                "name",
                "age",
                "favorite",
                "master",
                "botmaster",
                "creator",
                "inventor",
                "boss",
                "friend",
                "buddy",
                "pal",
                "nemesis",
                "birthday",
                "job",
                "occupation",
              }
            )
            or (
              has_poss_pronoun
              and bot_message.split()[0] in ("what", "how")
            )
          )
          and cats["entities"]
          in (
            (),
            ("alice",),
          )
          and cats["question"] == True
          and (has_poss_pronoun or "PRP$" in dict(cats["tagged"]).values())
        ):
          if new_response := await alice_response(bot_message, uid):
            return await respond(new_response)

        if (
          "age" in cats["attributes"]
          and cats["entities"]
          or "how long " in bot_message.lower()
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
          for pos in dict(cats["tagged"]).values()
          if pos in ("DT", "JJR", "PRP", "PRP$")
        )
        if exclaim_score >= 4:
          if new_response := await gpt_response(bot_message, uid):
            return await respond(new_response)

        if m := re.compile(
          "^(?:do you know |what is |what'?s |"
          "^ *)([0-9]+.*[0-9])[,?.]* *$",
          re.DOTALL | re.IGNORECASE,
        ).search(bot_message):
          try:
            return await respond(
              m.group(1) + " is " + str(eval(m.group(1).strip())) + "."
            )
          except:
            pass

        if not response:
          if not cats["question"] or (
            not cats["person"] and not cats["entities"]
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
        "\x0a".join(
          traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
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