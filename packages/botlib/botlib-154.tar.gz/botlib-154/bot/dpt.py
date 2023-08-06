# This file is placed in the Public Domain.


from .cbs import Cbs
from .obj import Object
from .fnc import register


class Dpt(Object):

    cmd = Object()
    events = []

    def __init__(self):
        Object.__init__(self)
        self.register("cmd", dispatch)

    def add(self, cmd):
        register(Cmd.cmd, cmd.__name__, cmd)

    def get(self, cmd):
        f =  get(Cmd.cmd, cmd)
        return f



def dispatch(e):
    try:
        e.parse()
        f = Cmd.get(e.cmd)
        if f:
            f(e)
            e.show()
    except (Restart, Stop):
        pass
    except Exception as ex:
        e.errors.append(ex)
    finally:
        e.ready()
