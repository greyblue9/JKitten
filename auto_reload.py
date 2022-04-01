def auto_reload_start(bot):
  import watchdog.observers, watchdog.events
  from pathlib import Path
  from importlib.machinery import all_suffixes
  
  path_as_dotted = lambda path: list(
    ".".join(p.parts[:-1] + (p.name.removesuffix(s),))
    for p in (
      Path(path).relative_to(Path.cwd()),
    )
    for s in all_suffixes()
    if p.name.endswith(s)
  )
  evts = []
  obs = watchdog.observers.Observer()
  h = type(
    "EvtHandler",
    (watchdog.events.FileSystemEventHandler,),
    {
      "on_modified": lambda self, evt: bot.reload_extension(
        path_as_dotted(evt.src_path)[0]
      ) if path_as_dotted(evt.src_path) else None
    },
  )()
  obs.schedule(event_handler=h, path=Path.cwd() / "commands", recursive=True)
  obs.start()
