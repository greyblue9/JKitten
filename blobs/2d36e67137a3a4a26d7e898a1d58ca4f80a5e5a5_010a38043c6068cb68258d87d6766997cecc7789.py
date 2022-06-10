from __main__ import *
from disnake.ext.commands.interaction_bot_base import CommonBotBase
from disnake.ext.commands import Cog
from disnake.ext.commands import Command
from pprint import pprint
import nltk
import aiohttp
from safeeval import SafeEval

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
  "I like a good discussion.",
  "I'm very enthusiastic.",
  "I'm sorry, I didn't mean to hurt your feelings.",
  "\"\"",
  "is .",
  "I'm sorry, I'm not a native speaker.",
  "where.",
  "what.",
  " is.",
  "is .",
  "when.",
  "who.",
}

import pprint
from pathlib import Path
import sys

last_input = last_response = ""


def get_chat(uid=DEFAULT_UID):
  return PyAimlChat(uid)
import __main__
__main__.get_chat = get_chat


class PyAimlChat:
  def __init__(self, uid=DEFAULT_UID):
    self.uid = uid
  def multisentenceRespond(self, query):
    resp = alice_response_inner(query, self.uid)
    if any(
      w.lower() in resp.lower() or resp.lower() in w.lower()
      for w in BLACKLIST
    ):
      log.info("Not using due to blacklist: %s", resp)
      resp = ""
      
    return resp.replace('is I.', 'is Alice').replace('I is', 'Alice is').replace('led I.', 'led Alice.')


def alice_response_inner(q, uid=DEFAULT_UID):
  from __main__ import get_kernel
  k = get_kernel() 
  log.info("alice_response_inner: q=%s", q)
  q2 = norm_sent(k, q)
  log.info("alice_response_inner: q2=%s", q2)
  r = k.respond(q2)
  log.info("alice_response_inner: r=%s", r)
  r2 = fix_pred_response(r) if " ." in r else r
  log.info("alice_response_inner: r2=%s", r2)
  return r2


def fix_pred_response(s):
  subj, key, *rest = s.partition(" .")[0].lower().split()
  ans = (
    k.getPredicate(key, subj)
    if subj not in ("my", "me", "i", "we", "myself")
    else k.getBotPredicate(key)
  )
  resp = (
    "".join([s.partition(" .")[0], " ", ans, "."])
    if ans
    else "".join(["What ", " ".join(rest), " ", subj, " ", key, "?"])
  )
  return resp


def norm_sent(k, s):
  import re

  exec(
    'for f,t in k._subbers["normal"].items(): s = re.sub(rf"\\b{re.escape(f)}\\b", t, s)',
    locals(),
  )
  norm = re.sub(
    r" ([^a-zA-Z0-9_])\1* *",
    "\\1",
    " ".join(
      filter(
        None,
        map(
          str.strip,
          re.split(
            r"(?:(?<=[a-zA-Z0-9_]))(?=[^a-zA-Z0-9_])|(?:(?<=[^a-zA-Z0-9_]))(?=[a-zA-Z0-9_])",
            s,
          ),
        ),
      )
    ),
  )
  return norm





async def alice_response(bot_message, uid=DEFAULT_UID):
  global chat
  chat = get_chat(uid)
  return chat.multisentenceRespond(bot_message)


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

last_model = None
async def get_response(message, uid, model=None):
  
  model = None
  print("*** in ", message, uid, model, responses.setdefault(uid,[""]))
  global last_model
  response = None
  inpt = bot_message = message
  data = {}
  for attempt in range(4):
    if response:
      return response
    print("?? in ", last_model)
    if last_model and (not last_input.lower().startswith("what") or ("they" in last_input.lower() or "them "in last_input.lower() or " it " in last_input.lower() or " he  " in last_input.lower() or " she  "in last_input.lower())):
        model = last_model
        log.info("reusing model %s", last_model)
        print("reuse model", last_model)
        last_model = None
    if not model:
      model = random.choices(
        model_names := ( 
          "microsoft/DialoGPT-large",
          "microsoft/DialoGPT-medium",
          "facebook/blenderbot-400M-distill",
          "deepparag/Aeona",
          "facebook/blenderbot-90M",
          "facebook/blenderbot-3B",
          "facebook/blenderbot_small-90M",
          "microsoft/DialoGPT-small",
        ),
        weights := (125, 15,15, 5,6,9,15,17),
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
    token = "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"
    headers = {"Authorization": f"Bearer {token}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
      "generated_responses": [],
      "past_user_inputs": [],
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
          await asyncio.sleep(data.get("estimated_time", 6))
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
        reply = data.get("generated_text")
        response = reply
        if not response:
          model = None
          last_model = None
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
        if any(
          w.lower() in response.lower()
          or response.lower() in w.lower()
          for w in BLACKLIST
        ):
          log.info("Not using due to blacklist: %s", response)
          response = ""
          continue
        break
  log.info("get_response(%s) returning %s", bot_message, response)
  if model: last_model = model
  return response

async def gpt_response(bot_message, uid=None):
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  log.debug("gpt_response(%r, %r)", bot_message, uid)

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
  log.info("query GPT for %r returns %r", bot_message, response)
  return response


async def google(bot_message, uid=None):
  return google2(bot_message, uid)
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  return google2(bot_message, uid)
  
from pprint import pprint
import functools

def strip_xtra(s):
  import codecs, re
  print("strip_xtra(%r)" % (s,))
  
  escaped = codecs.unicode_escape_encode(s)[0]
  print("strip_xtra(%r): escaped=%r" % (s, escaped))
  
  splits = re.compile(rb"[\t ][\t ]+|\\n|\\xb7|\\xa0", re.DOTALL).split(escaped)
  ok = []
  for i in splits:
    i = i.strip()
    if re.compile(rb"^[A-Z][a-z]{2} \d+(,|$)", re.DOTALL).search(i):
      continue
    if not re.compile(rb"([A-Z]*[a-z]+|[A-Z]+|[a-z]+|[A-Z]+[a-z]*) ", re.DOTALL).search(i):
      continue
    ok.append(i)
  if not ok:
    return ""
  ordered = sorted(ok, key=len)
  longest = ordered[-1]
  
  s0 = codecs.unicode_escape_decode(longest)
  print("strip_xtra(%r): s0=%r" % (s, s0))
  
  s1 = re.compile(
    "(?<=[^a-zA-Z])'((?:[^'.]|(?<=[a-z]))'[a-z]+)(\\.?)'",
    re.DOTALL
  ).sub("\\1", s0).strip()
  
  s2 = re.compile(
    "([a-z])'[a-z]*", re.DOTALL
  ).sub("\\1", s1).strip()
  return s2



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
  for idx, d in reversed(list(enumerate(descrips))):
    if " is " not in d.strip() and " are " not in d.strip() and " were " not in d.strip() and " was " not in d.strip() and " will " not in d.strip() and " has " not in d.strip() and " have " not in d.strip() and " can " not in d.strip():
      descrips.pop(idx)
  
  descrips = [strip_xtra(d) for d in descrips]
  print("descrips=", descrips)
  
  answers = [
    e[e.lower().index(strip_xtra(ans_marker).lower()) :]
    .strip(". ")
    .split(". ")[0]
    .split("\xa0")[0]
    for e in descrips
    if strip_xtra(ans_marker).lower() in e.lower()
  ]
  print("answers=", answers)
  
  answer = answers[-1] if answers else None
  try:
    next_url = "https://www.google.com{}".format(
      next(iter(doc.select('a[aria-label="Next page"]')))["href"]
    )
  except StopIteration:
    next_url = None
  
  return (
    (answer[0].upper() + answer[1:]).strip(" \n\t.")+"."
    if answer
    else (descrips[0][0].upper() + descrips[0][1:]).strip(" \n\t.")+"." if descrips
    else google2(bot_message, uid, next_url)
    if req_url is None and next_url
    else ""
  )


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
    global last_response
    global last_input
    response = ""
    channel_id = message.channel.id
    channel = message.channel
    in_whitelist = any(
      channel.name.lower() in f.lower() for f in CHANNEL_NAME_WHITELIST
    )
    print(f"channel.name = {channel.name}")
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
    content = message.content or message.system_content or "\n".join(filter(None, ((e.title + "\n" + e.description).strip() for e in message.embeds)))
    bot_message = " ".join(
      (replace_mention(word, name_lookup) for word in content.split())
    )
    if not message.author.bot and bot_message.strip().startswith("perkel"):
      await message.reply((bot_message + " ") + (bot_message + " "))
      return
    bot_message = translate_emojis(bot_message)
    if "https://" in bot_message or "http://" in bot_message:
      bot_message = translate_urls(bot_message)

    log.info(f"[{message.author.name}][{message.guild.name}]:" f" {bot_message}")
    mention = f"<@!{self.bot.user.id}>"
    if self.bot.user == message.author:
      return
    ok = (
      in_whitelist
      or self.bot.user in message.mentions
      or mention in content
      or "alice" in content.lower()
      or "alice " in bot_message.lower()
    )
    ok = ok and content[0:1].isalnum()
    if not ok:
      return

    def respond(new_response):
      nonlocal response
      response = new_response
      log.info("Responding to %r with %r", bot_message, response)
      inputs.setdefault(uid, []).append(bot_message)
      responses.setdefault(uid, []).append(response)
      global last_response
      global last_input
      if message.author.bot:
        response = f"<@{message.author.id}> {response}"
      last_input = bot_message
      last_response = response
      return message.reply(response)
    if message.author.id == self.bot.user.id:
      return
    from __main__ import get_kernel
    try:
      with message.channel.typing():
        bot_message = norm_sent(get_kernel(), bot_message)
        if (last_response.strip().endswith("?") and last_model):
          if new_response := await gpt_response(bot_message, uid):
            return await respond(new_response)
            
        if any(bot_message.lower().strip().startswith(w) for w in (
          "who is your",
          "who are your",
          "who was your",
          "what is your",
          "what are your",
          "what was your",
          "when is your",
          "what are your",
        )):
          if new_response := await alice_response(bot_message, uid):
            return await respond(new_response)
        log.info("norm_sent -> %s", bot_message)
        from tagger import categorize
        log.info("bot_message=%r", bot_message)
        cats: dict = categorize(bot_message.lower() or "")
        log.info("cats=%r", cats)
        # {
        #   "tagged": tagged, "items": items,
        #   "question": question, "person": person,
        #   "entities": tuple(entities),
        #   "attributes": tuple(attributes),
        #   "clauses": tuple(clauses),
        # {
        pprint(cats)
        by_pos = {pos: wd for wd, pos in cats["tagged"]}
        log.info("by_pos=%r", by_pos)
        from tagger import tag_meanings
        pronouns_pos = {
          pos for pos, m in tag_meanings.items() if "pro" in str(m).lower()
        }
        personal_pos = {
          pos for pos, m in tag_meanings.items() if "pers" in str(m).lower()
        }
        has_pronouns = pronouns_pos.intersection(by_pos)
        has_personal = personal_pos.intersection(by_pos)
        has_proper_noun = cats["proper_noun"]
        has_poss_pronoun = "PRP" in (
          pos[0:3] for word, pos in cats["tagged"]
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
          and cats["tagged"][0][0] in ("what", "who", "when", "where", "how", "why")
          and len(cats["tagged"]) > 1
          and cats["tagged"][1]
          and cats["tagged"][1][0] in ("is", "are", "were", "was", "has", "do," "does", "had")
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
          "^(?:alice|[,*]*|do you know |what is |what'?s |"
          "^ *)*(.*[0-9].*)[,?.]* *$",
          re.DOTALL | re.IGNORECASE,
        ).search(bot_message):
          try:
            return await respond(
              m.group(1) + " is " + str(SafeEval().safeEval(m.group(1).strip(), [])) + "."
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
      embed.add_field(name="Your message", value=content)
      embed.add_field(name="Translated message", value=bot_message)
      await message.reply(
        response,
        embed=embed,
      )
    else:
      if response:
        return await respond(response)
    finally:
      pass

