# -*- coding: utf-8 -*-
import threading


def singleton(cls):
    """
    A thread-safe singleton decorator that modifies the class"s __new__ method.
    This ensures compatibility with abc and super() in Python 2.

    :param cls: 要被装饰的类
    :type cls: class
    :return: 单例类
    :rtype: class
    """
    instances = {}
    lock = threading.Lock()
    original_new = cls.__new__

    def __new__(cls, *args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = original_new(cls, *args, **kwargs)
        return instances[cls]

    cls.__new__ = staticmethod(__new__)
    return cls