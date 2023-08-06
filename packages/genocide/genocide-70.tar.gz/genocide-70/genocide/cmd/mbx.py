# This file is placed in the Public Domain.


"mailbox commands"


import mailbox
import os
import time


from genocide.obj import Db, find, fntime, format, save, update
from genocide.hdl import Commands
from genocide.mbx import Email, to_date
from genocide.tme import elapsed


def cor(event):
    if not event.args:
        event.reply("cor <email>")
        return
    nr = -1
    for _fn, email in find("email", {"From": event.args[0]}):
        nr += 1
        txt = ""
        if len(event.args) > 1:
            txt = ",".join(event.args[1:])
        else:
            txt = "From,Subject"
        event.reply("%s %s %s" % (nr, format(email, txt, plain=True), elapsed(time.time() - fntime(email.__stp__))))


Commands.add(cor)


def eml(event):
    if not event.args:
        event.reply("eml <searchtxtinemail>")
        return
    nr = -1
    db = Db()
    for fn, o in db.all("email"):
        if event.rest in o.text:
            nr += 1
            event.reply("%s %s %s" % (nr, format(o, "From,Subject"), elapsed(time.time() - fntime(fn))))


Commands.add(eml)


def mbx(event):
    if not event.args:
        return
    fn = os.path.expanduser(event.args[0])
    event.reply("reading from %s" % fn)
    nr = 0
    if os.path.isdir(fn):
        thing = mailbox.Maildir(fn, create=False)
    elif os.path.isfile(fn):
        thing = mailbox.mbox(fn, create=False)
    else:
        return
    try:
        thing.lock()
    except FileNotFoundError:
        pass
    for m in thing:
        o = Email()
        update(o, m._headers)
        o.text = ""
        for payload in m.walk():
            if payload.get_content_type() == 'text/plain':
                o.text += payload.get_payload()
        o.text = o.text.replace("\\n", "\n")
        save(o)
        nr += 1
    if nr:
        event.reply("ok %s" % nr)


Commands.add(mbx)
