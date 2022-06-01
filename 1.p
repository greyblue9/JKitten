Index: commands/Chat.py
===================================================================
--- commands/Chat.py
+++ commands/Chat.py
@@ -68,36 +68,11 @@
   "when.",
   "who.",
 }

-import pprint
-from pathlib import Path
-import sys
-
 last_input = last_response = ""


-def get_chat(uid=DEFAULT_UID):
-  return PyAimlChat(uid)
-import __main__
-__main__.get_chat = get_chat
-
-
-class PyAimlChat:
-  def __init__(self, uid=DEFAULT_UID):
-    self.uid = uid
-  def multisentenceRespond(self, query):
-    resp = alice_response_inner(query, self.uid)
-    if any(
-      w.lower() in resp.lower() or resp.lower() in w.lower()
-      for w in BLACKLIST
-    ):
-      log.info("Not using due to blacklist: %s", resp)
-      resp = ""
-
-    return resp.replace('is I.', 'is Alice').replace('I is', 'Alice is').replace('led I.', 'led Alice.')
-
-
 def alice_response_inner(q, uid=DEFAULT_UID):
   from __main__ import get_kernel
   k = get_kernel()
   log.info("alice_response_inner: q=%s", q)
@@ -200,15 +175,13 @@
   return response


 last_model = None
-async def get_response(message, uid, model=None):
-
-  model = None
+async def get_response(bot_message, uid, model=None, message=None):
   print("*** in ", message, uid, model, responses.setdefault(uid,[""]))
   global last_model
   response = None
-  inpt = bot_message = message
+  inpt = bot_message
   data = {}
   for attempt in range(4):
     if response:
       return response
@@ -222,22 +195,22 @@
       model = random.choices(
         model_names := (
           "microsoft/DialoGPT-large",
           "microsoft/DialoGPT-medium",
+          "microsoft/DialoGPT-small",
+          "deepparag/Aeona",
           "facebook/blenderbot-400M-distill",
-          "deepparag/Aeona",
           "facebook/blenderbot-90M",
           "facebook/blenderbot-3B",
           "facebook/blenderbot_small-90M",
-          "microsoft/DialoGPT-small",
         ),
-        weights := (125, 15,15, 5,6,9,15,17),
+        weights := (225, 15,15, 5,6,9,15,17),
       )[0]
       model_idx = model_names.index(model)
       weight = weights[model_idx]
       log.info(
       "\nget_response(%r, %r): selected model\n\n" "    %r   (weight: %s)\n\n",
-      message,
+      bot_message,
       uid,
       model,
       weight,
       )
@@ -246,9 +219,9 @@
     API_URL = f"https://api-inference.huggingface.co/models/{model}"
     payload = {
       "generated_responses": [],
       "past_user_inputs": [],
-      "text": message,
+      "text": bot_message,
     }
     context = random.randint(0, 4)
     if context > 3:
       payload["generated_responses"] += responses.setdefault(uid, [])[-2:]
@@ -269,10 +242,15 @@
         else:
           pprint(data)
         if not data:
           data = {"error": "No reply", "estimated_time": 5}
-        if data.get("error"):
-          await asyncio.sleep(data.get("estimated_time", 6))
+        if data.get("estimated_time"):
+          sleepytime = data.get("estimated_time", 0)
+          if sleepytime:
+            import time
+            ts = int(time.time() + sleepytime)
+            await message.reply(f"Please wait <t:{ts}:R>, I am working on a response ...", delete_after=sleepytime)
+            await asyncio.sleep(sleepytime)
           async with ClientSession() as session:
             async with session.post(
               API_URL, headers=headers, json=payload
             ) as response:
@@ -314,14 +292,14 @@
   if model: last_model = model
   return response


-async def gpt_response(bot_message, uid=None):
+async def gpt_response(bot_message, uid=None, message=message):
   if uid is None:
     from __main__ import DEFAULT_UID as uid
   log.debug("gpt_response(%r, %r)", bot_message, uid)

-  response = await get_response(bot_message, uid)
+  response = await get_response(bot_message, uid=uid, message=message)
   if not response:
     return ""
   for b in BLACKLIST:
     if b.lower() in response.lower() or response.lower() in b:
@@ -729,9 +707,9 @@
         if not USE_JAVA and not hasattr(__main__, "Chat"):
           from __main__ import get_kernel
           bot_message = norm_sent(get_kernel(), bot_message)
         if (last_response.strip().endswith("?") and last_model):
-          if new_response := await gpt_response(bot_message, uid):
+          if new_response := await gpt_response(bot_message, uid, message):
             return await respond(new_response)

         if any(bot_message.lower().strip().startswith(w) for w in (
           "who is your",
@@ -864,9 +842,9 @@
           for pos in dict(cats["tagged"]).values()
           if pos in ("DT", "JJR", "PRP", "PRP$")
         )
         if exclaim_score >= 4:
-          if new_response := await gpt_response(bot_message, uid):
+          if new_response := await gpt_response(bot_message, uid, message):
             return await respond(new_response)

         if m := re.compile(
           "^(?:alice|[,*]*|do you know |what is |what'?s |"
@@ -883,9 +861,9 @@
         if not response:
           if not cats["question"] or (
             not cats["person"] and not cats["entities"]
           ):
-            if new_response := await gpt_response(bot_message, uid):
+            if new_response := await gpt_response(bot_message, uid, message):
               response = new_response

           elif new_response := await wolfram_alpha(bot_message, uid):
             return await respond(new_response)
