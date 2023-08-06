# This file is placed in the Public Domain.


"table"


import inspect
import os
import sys
import unittest


from bot.obj import Object, keys, values
from bot.tbl import Tbl


import bot.bsc


Tbl.add(bot.bsc)


class Test_Table(unittest.TestCase):

    def test_mod(self):
        self.assertTrue("bot.bsc" in keys(Tbl.mod))
