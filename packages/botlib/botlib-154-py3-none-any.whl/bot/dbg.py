# This file is placed in the Public Domain.


from bot.cmd import Cmd
from bot.err import Restart, Stop
from bot.lop import Loop


def rse(event):
    raise Restart


Cmd.add(rse)
