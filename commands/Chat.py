from __main__ import get_chat, pos_tag, replace_mention
from text_tools import translate_emojis, translate_urls
from typing import Optional, Union, Any
import random, requests, asyncio, re, logging, sys, traceback, time, json
from aiohttp import ClientSession
from __main__ import *
from disnake.ext.commands.interaction_bot_base import CommonBotBase
from disnake.ext.commands import Cog
from disnake.ext.commands import Command
from pprint import pprint
import nltk
import aiohttp
import inspect
from safeeval import SafeEval
from bs4 import BeautifulSoup as BS
from bs4 import BeautifulSoup
from tagger import categorize

from __main__ import DEFAULT_UID, log, inputs, responses
from disnake import BotIntegration, Color, Embed, Message
from tagger import tag_meanings

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
  'reference to the song', 'is unknown.', "I'm over hereactly", ' is .', 'as a contact', 'is an enity', 'or not. I am', 'I like a good discussion.', 'making a video', 'I try to keep my life in balance.', 'I know, right', 'Thanks for the trade', "I'm not sure what you're trying to say", 'is .', 'search the web', 'serious or not', 'a guy making a video ', 'is what.', 'Are you a girl', 'good song', 'is the guy who made the video', "I'm very enthusiastic.", 'Let me learn this', 'JSFAILED', 'joking or not', 'Last Airbender', 'place a call', 'not sure what you mean', 'want to talk about unknown', 'where.', 'the last of us', 'SRAIXFAILED', "I'm sorry, I'm not a native speaker.", 'a web search', 'album by', '·',
  
}

last_input = last_response = ""


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
  from __main__ import get_kernel
  k = get_kernel()
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
  if k:
    for f,t in k._subbers["normal"].items():
      s = re.sub(rf"\b{re.escape(f)}\b", t, s)
  
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



async def wolfram_alpha(inpt, uid=None):
  if len(inpt.split()) < 3:
    return ""
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  log.info("wolfram_alpha(%r, %r) query", inpt, uid)
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
  log.info("wolfram_alpha(%r, %r) returning %r", inpt, uid, response)
  if any(
    w.lower() in response.lower()
    or response.lower() in w.lower()
    for w in BLACKLIST
  ):
    log.info("Not using due to blacklist: %s", response)
    return ""
  return response


last_model = None
async def get_response(bot_message, uid, model=None, message:Message=None): #type: ignore
  print("*** in ", message, uid, model, responses.setdefault(uid,[""]))
  global last_model
  response = None
  inpt = bot_message
  data = {}
  for attempt in range(4):
    if response:
      return response
    print("?? in ", last_model)
    if last_model and (not last_input.lower().startswith("what") or ("they" in last_input.lower() or "them "in last_input.lower() or " it " in last_input.lower() or " he  " in last_input.lower() or " she  "in last_input.lower() or "you" in last_input.lower() or "can " in last_input.lower())):
        model = last_model
        log.info("reusing model %s", last_model)
        print("reuse model", last_model)
    if not model:
      model = random.choices(
        model_names := ((
          "microsoft/DialoGPT-large",
          "microsoft/DialoGPT-medium",
          "microsoft/DialoGPT-small",
          "facebook/blenderbot-400M-distill",
          "facebook/blenderbot-90M",
          "facebook/blenderbot_small-90M",
        ) if not (is_question := bot_message.lower().split()[0] in ("what", "where", "when")) else (
          "deepset/roberta-base-squad2",
          "ahotrod/albert_xxlargev1_squad2_512",
          "deepset/bert-large-uncased-whole-word-masking-squad2",
        )),
        weights := ((
          325, 15, 15, 6, 9, 17
        ) if not is_question else (
          33, 33, 33
        )),
      )[0]
      model_idx = model_names.index(model)
      weight = weights[model_idx]
      log.info(
      "\nget_response(%r, %r): selected model\n\n" "    %r   (weight: %s)\n\n",
      bot_message,
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
      "text": bot_message,
    }
    context = random.randint(0, 4)
    if context > 3:
      payload["generated_responses"] += responses.setdefault(uid, [])[-2:]
    elif context > 2:
      payload["generated_responses"] += responses.setdefault(uid, [])[-1:]
    if context > 1:
      payload["past_user_inputs"] += inputs.setdefault(uid, [])[-1:]
    async with ClientSession() as session:
      async with session.post(API_URL, headers=headers, json=payload) as response:
        try:
          data = await response.json()
        except aiohttp.client_exceptions.ContentTypeError:  # type: ignore
          print(response.content)
          try:
            data = await response.json(content_type="application/json")
          except Exception as e:
            print(e)
        else:
          pprint(data)
        if not data:
          data = {"error": "No reply", "estimated_time": 5}
        if data.get("estimated_time"):
          sleepytime = data.get("estimated_time", 0)
          if sleepytime:
            import time
            ts = int(time.time() + sleepytime)
            await message.reply(f"Please wait <t:{ts}:R>, I am working on a response ...", delete_after=sleepytime)
            await asyncio.sleep(sleepytime)
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
        if response.lower() == bot_message.lower():
          response = ""
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


async def gpt_response(bot_message, uid=None, message=None):
  uid = uid or DEFAULT_UID
  log.debug("gpt_response(%r, %r)", bot_message, uid)

  response = await get_response(bot_message, uid=uid, message=message)
  if not response:
    return ""
  if response.lower() == bot_message.lower():
    response = ""
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
  if len(bot_message.split()) < 3:
    return ""
  import __main__
  from __main__ import Class, USE_JAVA
  if not USE_JAVA:
    return ""
  if uid is None:
    from __main__ import DEFAULT_UID as uid
  log.debug("google(%r, %r) called", bot_message, uid)
  from __main__ import get_chat
  chat = get_chat(uid)
  if inspect.isawaitable(chat):
    chat = await chat
  cats = categorize(bot_message.lower())
  topic = cats["entities"][0] if cats["entities"] else "*"
  Sraix = Class.forName("org.alicebot.ab.Sraix")
  response = Sraix.sraixPannous(bot_message, topic, chat.chat if hasattr(chat, "chat") else chat)
  if "SRAIXFAILED" in response:
    log.debug("google(%r, %r) failed with %r", bot_message, uid, response)
    return ""
  if response.lower() == bot_message.lower():
    response = ""
  for b in BLACKLIST:
    if b.lower() in response.lower() or response.lower() in b:
      log.debug(
        "google(%r, %r) discarding response %r because it repeats a previous entry",
        bot_message,
        uid,
        response,
      )
      return ""
  log.info("query Google for %r returns %r", bot_message, response)
  return response


import functools

def strip_xtra(s):
  import codecs, re
  print("strip_xtra(%r)" % (s,))

  escaped = codecs.unicode_escape_encode(s)[0]  # type: ignore
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

  s0 = codecs.unicode_escape_decode(longest)[0]  # type: ignore
  print("strip_xtra(%r): s0=%r" % (s, s0))

  s1 = re.compile(
    "(?<=[^a-zA-Z])'((?:[^'.]|(?<=[a-z]))'[a-z]+)(\\.?)'",
    re.DOTALL
  ).sub("\\1", s0).strip()

  return re.compile("([a-z])'[a-z]*", re.DOTALL).sub("\\1", s1).strip()


def find(coll, r):
  return (
    [coll[idx + 1 :] + coll[idx : idx + 1] for idx, w in enumerate(coll) if w in r][
      0
    ]
    if any(w in coll for w in r)
    else coll
  )


def google2(bot_message, uid="0", req_url=None):
  if len(bot_message.split()) < 3:
    return ""
  try:
    ans_marker = " ".join(
      find(
        re.subn("[.?!\t\n ]*$", "", bot_message.lower())[0].split(),
        ("is", "are," "were", "was"),
      )
    )

    query = f'"{ans_marker}"'
  except Exception:
    ans_marker = bot_message
    query = bot_message
  from bs4 import BeautifulSoup
  from pathlib import Path
  from urllib.request import Request, urlopen
  from urllib.parse import quote_plus

  if not req_url:
    req_url = f"https://www.google.com/search?client=safari&rls=en&gbv=1&q={quote_plus(query)}&hl=en&num=10"

  headers = {
    "Accept-Language": "en-us",
    "Host": "www.google.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko)Version/14.0.3 Safari/605.1.15",
  }

  request = urlopen(Request(req_url, headers=headers))
  html = request.read()
  request.close()

  doc = BeautifulSoup(html, "html.parser")
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
    if "'?" in d or "?'" in d or (" is " not in d.strip() and " are " not in d.strip() and " were " not in d.strip() and " was " not in d.strip() and " will " not in d.strip() and " has " not in d.strip() and " have " not in d.strip() and " can " not in d.strip()):
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
  answers = sorted(answers, key=lambda a: (a[0].isupper() and (a[1:2].islower() or a.split()[1][0:1].islower())) * 8 + (a.strip().endswith(".")) * 6 + (" ago — " not in a) * 4 + ("›" not in a) * 12 + ("..." not in a) * 6)
  
  if not answers:
    for a in descrips:
      a2 = strip_xtra(a)
      if not a2: continue
      answers.append(a2)
  print("answers=", answers)
  answers = sorted(answers, key=lambda a: (a[0].isupper() and (a[1:2].islower() or a.split()[1][0:1].islower())) * 8 + (a.strip().endswith(".")) * 6 + (" ago — " not in a) * 4 + ("›" not in a) * 12 + ("..." not in a) * 6)
  answer = answers[-1] if answers else None
  try:
    next_url = "https://www.google.com{}".format(
      next(iter(doc.select('a[aria-label="Next page"]')))["href"]
    )
  except StopIteration:
    next_url = None
  descrips = sorted(descrips, key=lambda a: (a[0].isupper() and (a[1:2].islower() or a.split()[1][0:1].islower())) * 8 + (a.strip().endswith(".")) * 6 + (" ago — " not in a) * 4 + ("›" not in a) * 12 + ("..." not in a) * 6)
  a = (
    answer
    if answer
    else descrips[-1] if descrips
    else google(bot_message, uid)
  )
  if a.lower() == bot_message.lower():
    return ""
  if any(b in a for b in BLACKLIST):
    return ""
  return a


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



last_input = last_response = ""
use_alice = False
from __main__ import name_lookup

class ChatCog(Cog):
  bot: BotIntegration
  event = Cog.listener()

  def __init__(self, bot):
    self.bot = bot
    super().__init__()

  @Command
  async def wa(self, ctx, *, message):
    response = await wolfram_alpha(message)
    return await ctx.send(response)

  @Command
  async def ip(self, ctx, *, message=""):
    ip = requests.get("https://ip.me").text
    await ctx.reply(f"My IP is {ip}")

  @Command
  async def blacklist(self, ctx, *, message):
    global BLACKLIST
    BLACKLIST.add(message)
  
  @Command
  async def google(self, ctx, *, message):
    response = google2(message)
    return await ctx.send(response)
  
  @Command
  async def alice(self, ctx, *, message):
    response = await alice_response(message, str(ctx.message.author.id))
    return await ctx.send(response)
  
  @event
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
def setup(bot):
  cog = ChatCog(bot)
  bot.add_cog(cog)
  return cog
