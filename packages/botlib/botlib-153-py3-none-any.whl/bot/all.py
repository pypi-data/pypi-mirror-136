# This file is placed in the Public Domain.


"bot package modules"


from bot.tbl import Tbl


from bot import cfg
from bot import cmd
from bot import dbs
from bot import evt
from bot import flt
from bot import fnc
from bot import jsn
from bot import krn
from bot import opt
from bot import prs
from bot import rpt
from bot import sta
from bot import tbl
from bot import thr
from bot import tmr


Tbl.add(cfg)
Tbl.add(cmd)
Tbl.add(dbs)
Tbl.add(evt)
Tbl.add(flt)
Tbl.add(fnc)
Tbl.add(jsn)
Tbl.add(krn)
Tbl.add(opt)
Tbl.add(prs)
Tbl.add(rpt)
Tbl.add(sta)
Tbl.add(tbl)
Tbl.add(thr)
Tbl.add(tmr)


from bot import fnd
from bot import irc
from bot import log
from bot import opt
from bot import rss
from bot import tdo
from bot import udp
from bot import usr


Tbl.add(fnd)
Tbl.add(irc)
Tbl.add(log)
Tbl.add(opt)
Tbl.add(rss)
Tbl.add(tdo)
Tbl.add(udp)
Tbl.add(usr)
