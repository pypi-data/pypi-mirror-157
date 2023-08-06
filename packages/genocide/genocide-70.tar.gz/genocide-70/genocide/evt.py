# This file is placed in the Public Domain.


"event"


import threading


from .obj import Object
from .hdl import Bus


def __dir__():
    return (
        "Command",
        "Event"
    )


class Event(Object):

    def __init__(self):
        super().__init__()
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.args = []
        self.channel = ""
        self.cmd = ""
        self.gets = Object()
        self.orig = ""
        self.index = None
        self.rest = ""
        self.sets = Object()
        self.txt = ""
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self, txt=None, orig=None):
        self.txt = txt or self.txt
        self.orig = orig or self.orig
        if self.txt:
            spl = self.txt.split()
            args = []
            _nr = -1
            hasarg = False
            for w in spl:
                _nr += 1
                if _nr == 0:
                    try:
                        self.index = int(w[1:])
                    except ValueError:
                        self.cmd = w
                    continue
                try:
                    k, v = w.split("==")
                    self.gets[k] = v
                except ValueError:
                    hasarg = True
                try:
                    k, v = w.split("=")
                    self.sets[k] = v
                except ValueError:
                    hasarg = True
                if hasarg:
                    args.append(w)
            if args:
                self.args = args
                self.rest = " ".join(args)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self._result.append(txt)

    def show(self):
        assert self.orig
        for txt in self._result:
            Bus.say(self.orig, self.channel, txt)

    def wait(self):
        self._ready.wait()
        for thr in self._thrs:
            thr.join()
        return self._result


class Command(Event):

    def __init__(self):
        Event.__init__(self)
        self.type = "command"
        