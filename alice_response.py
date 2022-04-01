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
