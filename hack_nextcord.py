from nextcord.client import *
from typing import *
import asyncio
import logging
_log = logging.getLogger(__name__)

def _cleanup_loop(loop):
  pass

def run(self, *args: Any, **kwargs: Any) -> None:
  """A blocking call that abstracts away the event loop
  initialisation from you.

  If you want more control over the event loop then this
  function should not be used. Use :meth:`start` coroutine
  or :meth:`connect` + :meth:`login`.

  Roughly Equivalent to: ::

    try:
      loop.run_until_complete(start(*args, **kwargs))
    except KeyboardInterrupt:
      loop.run_until_complete(close())
      # cancel all tasks lingering
    finally:
      loop.close()

  .. warning::

    This function must be the last function to call due to the fact that it
    is blocking. That means that registration of events or anything being
    called after this function call will not execute until it returns.
  """
  loop = self.loop

  try:
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
  except NotImplementedError:
    pass
  except:
    pass

  async def runner():
    try:
      await self.start(*args, **kwargs)
    finally:
      if not self.is_closed():
        await self.close()

  def stop_loop_on_completion(f):
    loop.stop()

  future = asyncio.ensure_future(runner(), loop=loop)
  future.add_done_callback(stop_loop_on_completion)
  try:
    loop.run_forever()
  except KeyboardInterrupt:
    _log.info("Received signal to terminate bot and event loop.")
  finally:
    future.remove_done_callback(stop_loop_on_completion)
    _log.info("Cleaning up tasks.")
    _cleanup_loop(loop)

  if not future.cancelled():
    try:
      return future.result()
    except KeyboardInterrupt:
      # I am unsure why this gets raised here but suppress it anyway
      return None

Client.run = run 
