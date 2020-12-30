# -*- coding: utf-8 -*-
from threading import Thread


def make_thread(func, is_daemon=True) -> Thread:
    thread = Thread(target=func)
    thread.daemon = is_daemon
    thread.start()
    return thread
