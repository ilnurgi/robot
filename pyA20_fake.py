# coding: utf-8
"""
мок модуль
"""

from time import time


class gpio(object):
    """"""

    HIGH = 1
    LOW = 0

    OUTPUT = INPUT = PULLDOWN = None

    @staticmethod
    def init():
        """"""

    @staticmethod
    def setcfg(*args):
        """"""

    @staticmethod
    def pullup(*args):
        """"""

    @staticmethod
    def output(*args):
        """"""


class port(object):
    """"""

    PG0 = None


class i2c(object):
    """"""

    @staticmethod
    def init(address):
        """"""

    @staticmethod
    def open(port):
        """"""

    @staticmethod
    def read(count):
        """"""
        t = str(time())
        # at
        values = [97, 116]
        # bat
        values.extend((0, int(t[:3])))
        # temp
        values.extend(divmod(int(t[3:6]), 256))
        # photo
        values.extend(divmod(int(t[6:9]), 256))
        # other
        values.extend((0, 0, 0, 0, 0, 0, 0, 0))
        return values

    @staticmethod
    def write():
        """"""
