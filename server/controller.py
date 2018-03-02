# coding: utf-8
"""
контроллер
"""

from time import time

try:
    from pyA20 import i2c
except ImportError:
    from pyA20_fake import i2c

import settings


class Controller(object):

    def __init__(self, device_address, port):
        i2c.init(device_address)
        i2c.open(port)

    def read_values(self):
        """
        читаем данные с контроллера
        """
        values = i2c.read(settings.I2C_READ_BYTES_COUNT)

        if values[:2] != [97, 116]:
            return None

        return [
            # время актуальности
            int(time()),
            # батарея
            values[2] * 256 + values[3],
            # температура
            values[4] * 256 + values[5],
            # фото
            values[6] * 256 + values[7]
        ]