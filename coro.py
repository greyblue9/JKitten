def iter_over_async(ait, loop):
  ait = ait.__aiter__()
  done = False
  from threading import Event
  from asyncio import Future, ensure_future
  async def get_next():
    nonlocal done
    try:
      obj = await ait.__anext__()
      print("got obj=", obj)
      return obj
    except StopAsyncIteration:
      done = True
  while not done:
    if not loop.is_running():
      yield loop.run_until_complete(get_next())
    else:
      event = Event()
      fut = ensure_future(get_next())
      while not fut.done():
        Event().wait(0)
      yield fut.result()
    if done:
      break


def run_coro(coro, loop):
  from asyncio import ensure_future, gather
  from threading import Event
  from asyncio.exceptions import InvalidStateError
  fut = ensure_future(loop.create_task(coro))
  g = gather(fut)
  sentinel = object()
  def getter():
    while True:
      yield sentinel
      try:
        yield g.result()
        break
      except InvalidStateError:
        pass
      try:
        yield g.exception()
        break
      except InvalidStateError:
        pass
  return next(filter(lambda o: o is not sentinel, getter()))
