# This file is placed in the Public Domain.


"model commands"


import time


from ..obj import get
from ..hdl import Bus, Commands
from ..tme import elapsed


from genocide.mdl import aliases, nr, oorzaken, seconds, starttime, year


def now(event):
    delta = time.time() - starttime
    txt = elapsed(delta) + " "
    for name in sorted(oorzaken, key=lambda x: seconds(nr(x))):
        needed = seconds(nr(name))
        nrtimes = int(delta/needed)
        txt += "%s: %s " % (get(aliases, name), nrtimes)
    txt += " http://genocide.rtfd.io"
    Bus.announce(txt)


Commands.add(now)


def sts(event):
    name = event.rest or "psyche"
    needed = seconds(nr(name))
    if needed:
        delta = time.time() - starttime
        nrtimes = int(delta/needed)
        nryear = int(year/needed)
        txt = "patient #%s died from %s (%s/year) every %s" % (nrtimes, get(aliases, name),  nryear, elapsed(needed))
        Bus.announce(txt)


Commands.add(sts)


def tpc(event):
    txt = "%ss " % elapsed(time.time() - starttime)
    for name in sorted(oorzaken, key=lambda x: seconds(nr(x))):
        needed = seconds(nr(name))
        delta = time.time() - starttime
        nrtimes = int(delta/needed)
        if nrtimes < 30000:
            continue
        txt += "%s %s " % (get(aliases, name), nrtimes)
    for bot in Bus.objs:
        try:
            for channel in bot.channels:
                bot.topic(channel, txt)
        except AttributeError:
            pass


Commands.add(tpc)
