# This file is placed in the Public Domain.


"scan modules"


import importlib
import inspect
import os
import sys
import termios
import traceback


from .obj import Class, spl
from .hdl import Callbacks, Commands


class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)


def init(pns):
    for pn in spl(pns):
        mod = importlib.import_module(pn)
        if "init" in dir(mod):
            mod.init()


def init2(mns):
    for mn in spl(mns):
        mod = Table.get(mn)
        if mod and "init" in dir(mod):
            try:
                mod.init()
            except Exception as ex:
                Callbacks.errors.append(ex)


def introspect(mod):
    for k, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames[:o.__code__.co_argcount]:
            Commands.cmd[k] = o
    for k, clz in inspect.getmembers(mod, inspect.isclass):
        Class.add(clz)


def scan(dn, intro=False):
    mods = []
    for mod in scandir(dn):
        if intro:
            introspect(mod)
        Table.add(mod)
        mods.append(mod)
    return mods


def scandir(dn):
    dns = []
    if "." in dn:
        pn = dn
    else:
        pn = dn.split(os.sep)[-1]
    if os.path.exists(dn):
        dns.append(dn)
        sys.path.insert(0, dn)
    if not dns:
        try:
            pkg = importlib.import_module(dn)
            if pkg:
                if pkg.__file__:
                    dns.append(os.path.dirname(pkg.__file__))
                else:
                    dns.extend(pkg.__path__)
        except Exception as ex:
            dns = [dn,]
            Callbacks.errors.append(ex)
    result = []
    for dnn in dns:
        if not os.path.exists(dnn):
            continue
        for mn in os.listdir(dnn):
            if skip(mn):
                continue
            mn = mn[:-3]
            try:
                result.append(importlib.import_module(mn, pn))
            except Exception as ex:
                Callbacks.errors.append(ex)
    return result


def skip(fn):
    if not fn.endswith(".py"):
        return True
    if fn.endswith("~"):
        return True
    if fn.endswith("__.py"):
        return True
    return False


def wrap(func):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        for err in Callbacks.errors:
            traceback.print_exception(type(err), err, err.__traceback__)
