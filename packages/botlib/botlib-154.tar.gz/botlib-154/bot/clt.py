# This file is placed in the Public Domain.


"client"


from .bus import Bus
from .cbs import Cbs
from .cmd import dispatch
from .lop import Loop
from .obj import Object


def __dir__():
    return (
        "Client"
    )


class Client(Loop):

    def __init__(self):
        Loop.__init__(self)
        Bus.add(self)
        
    def announce(self, txt):
        self.raw(txt)

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)
