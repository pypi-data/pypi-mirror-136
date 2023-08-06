# This file is placed in the Public Domain.


"loop"


import queue
import time
import _thread


from .cbs import Cbs
from .cmd import dispatch
from .err import Stop
from .evt import Event
from .obj import Object
from .thr import launch
from .utl import locked


def __dir__():
    return (
        "Loop"
    )


class Loop(Object):


    def __init__(self):
        Object.__init__(self)
        self.errors = []
        self.queue = queue.Queue()
        self.stopped = False
        self.register("event", dispatch)

    def event(self, txt, origin=None):
        e = Event()
        e.type = "event"
        e.orig = repr(self)
        e.origin = origin or "user@handler"
        e.txt = txt
        return e

    def handle(self, e):
        e.thrs.append(launch(Cbs.callback, self, e, name=e.txt))

    def loop(self):
        while not self.stopped:
            try:
                e = self.poll()
                if not e:
                    break
                self.handle(e)
            except Restart:
                self.restart()
            except Stop:
                break

    def poll(self):
        return self.queue.get()

    def put(self, e):
        self.queue.put_nowait(e)

    def register(self, typ, cb):
        Cbs.add(typ, cb)

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        self.stopped = False
        launch(self.loop)

    def stop(self):
        self.stopped = True
        self.queue.put(None)
