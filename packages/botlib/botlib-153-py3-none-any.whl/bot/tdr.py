# This file is placed in the Public Domain.


from .evt import Event
from .krn import Cfg
from .obj import Object
from .tbl import Cmd
from .thr import launch


errors = []
events = []
param = Object()
param.add = ["test@shell", "bart", ""]
param.cfg = ["server=localhost", ""]
param.dne = ["test4", ""]
param.rem = ["reddit", ""]
param.dpl = ["reddit title,summary,link", ""]
param.log = ["test1", ""]
param.flt = ["0", ""]
param.fnd = ["cfg", "log", "rss", "log txt==test", "cfg server==localhost", "rss rss==reddit"]
param.rss = ["https://www.reddit.com/r/python/.rss"]
param.tdo = ["test4", ""]
skip = ["tinder"]


def consume(events):
    fixed = []
    res = []
    have = []
    for e in events:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            events.remove(f)
        except ValueError:
            continue


def payload(c):
    thrs = []
    for cmd in Cmd.cmd:
        if cmd in skip:
            continue
        for ex in getattr(param, cmd, [""]):
            e = Event()
            e.type = "cmd"
            e.txt = cmd + " " + ex
            e.orig = repr(c)
            thrs.append(launch(Cmd.handle, e))
            events.append(e)
    return thrs


def tdr(event):
    oldwd = Cfg.wd
    Cfg.wd = ".test"
    Cfg.debug = True
    nr = event.index or 10
    clt = event.bot()
    for x in range(nr):
        payload(clt)
    consume(events)
    Cfg.wd = oldwd


Cmd.add(tdr)
