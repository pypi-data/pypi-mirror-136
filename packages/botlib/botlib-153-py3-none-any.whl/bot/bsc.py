# This file is placed in the Public Domain.


"basic"


import threading
import time


from bot.bus import Bus
from bot.cls import Cls
from bot.cmd import Cmd
from bot.dbs import Db, fntime, save
from bot.dbs import find
from bot.fnc import format
from bot.obj import Object, get, keys, update
from bot.thr import getname
from bot.prs import elapsed


def __dir__():
    return (
        "Log",
        "cmd",
        "err",
        "flt",
        "fnd",
        "log",
        "tdo",
        "thr",
        "upt"
    )


starttime = time.time()


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def cmd(event):
    event.reply(",".join((sorted(keys(Cmd.cmd)))))


def err(event):
    if not Cmd.events:
        event.reply("no errors")
        return
    event.reply("%s events had errors" % len(Cmd.events))
    for e in Cmd.events:
        for err in e.errors:
            event.reply(err)


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(Bus.objs[index])
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(" | ".join([getname(o) for o in Bus.objs]))


def fnd(event):
    if not event.args:
        db = Db()
        res = ",".join(
            sorted({x.split(".")[-1].lower() for x in db.types()}))
        if res:
            event.reply(res)
        return
    otype = event.args[0]
    nr = -1
    got = False
    for fn, o in find(otype):
        nr += 1
        txt = "%s %s" % (str(nr), format(o))
        if "t" in event.opts:
            txt = txt + " %s" % (elapsed(time.time() - fntime(fn)))
        got = True
        event.reply(txt)
    if not got:
        event.reply("no result")

def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    save(o)
    event.reply("ok")


def thr(event):
    result = []
    for t in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(t).startswith("<_"):
            continue
        o = Object()
        update(o, vars(t))
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = t.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s(%s)" % (txt, elapsed(up)))
    if res:
        event.reply(" ".join(res))


def tdo(event):
    if not event.rest:
        event.reply("tdo <txt>")
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")


def upt(event):
    event.reply(elapsed(time.time() - starttime))


Cls.add(Log)
Cls.add(Todo)
Cmd.add(cmd)
Cmd.add(err)
Cmd.add(flt)
Cmd.add(fnd)
Cmd.add(log)
Cmd.add(tdo)
Cmd.add(thr)
Cmd.add(upt)
