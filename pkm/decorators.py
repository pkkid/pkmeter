# -*- coding: utf-8 -*-
"""
PKMeter Decorators
"""
import queue, threading
from pkm import log


def never_raise(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            log.exception(err)
    return wrap


class threaded_method(object):

    def __init__(self, func):
        self._func = func
        self._threads = {}
        self._queues = {}

    def __get__(self, inst, owner):
        if inst is None:
            return self
        key = self._func.__get__(inst, type(inst))
        if key not in self._queues:
            self._queues[key] = queue.Queue()
            self._threads[key] = threading.Thread(target=self._thread_loop, args=[inst, key])
            self._threads[key].daemon = True
            self._threads[key].start()
        return lambda *a, **k: self._queues[key].put((a, k))

    def _thread_loop(self, inst, key):
        while True:
            args = self._queues[key].get()
            try:
                self._func(inst, *args[0], **args[1])
            except Exception as err:
                log.error('Error in threaded func %s: %s' % (key.__name__, err))
