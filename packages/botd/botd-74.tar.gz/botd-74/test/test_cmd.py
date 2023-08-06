# This file is placed in the Public Domain.


"command"


import inspect
import unittest


from bot.cbs import Cbs
from bot.cls import Cls
from bot.cmd import Cmd
from bot.evt import Event
from bot.fnc import format
from bot.hdl import Handler, dispatch
from bot.krn import Cfg
from bot.obj import Object, get, values
from bot.tbl import Tbl
from bot.thr import launch


events = []


param = Object()
param.add = ["test@shell", "bart", ""]
param.cfg = ["nick=botje", "server=localhost", ""]
param.dlt = ["root@shell"]
param.dne = ["test4", ""]
param.dpl = ["reddit title,summary,link"]
param.flt = ["0", ""]
param.fnd = ["cfg", "log", "rss", "cfg server==localhost", "rss rss==reddit"]
param.log = ["test1", ""]
param.met = ["root@shell"]
param.nck = ["botje"]
param.pwd = ["bart blabla"]
param.rem = ["reddit", ""]
param.rss = ["https://www.reddit.com/r/python/.rss"]
param.tdo = ["things todo"]


class CLI(Handler):

     def __init__(self):
         Handler.__init__(self)

     def raw(self, txt):
         if Cfg.verbose:
             print(txt)
        
         
c = CLI()


def consume(events):
    fixed = []
    res = []
    for e in events:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            events.remove(f)
        except ValueError:
            continue
    return res


class Test_Commands(unittest.TestCase):

    def setUp(self):
        c.start()
        
    def tearDown(self):
        c.stop()

    def test_commands(self):
        cmds = sorted(Cmd.cmd)
        for cmd in cmds:
            for ex in getattr(param, cmd, [""]):
                e = Event()
                e.txt = cmd + " " + ex
                e.orig = repr(c)
                launch(Cbs.callback(e))
                events.append(e)
        consume(events)
        self.assertTrue(not events)
