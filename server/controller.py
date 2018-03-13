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

    def write_values(self, lt_value, rt_value, r_x, r_y, lb, rb, axis_b_l, axis_b_r):
        """
        записывает данные в контроллер
        :param values:
        """
        val_11, val_12 = divmod(lt_value, 256)
        val_21, val_22 = divmod(rt_value, 256)
        val_31, val_32 = divmod(r_x, 256)
        val_41, val_42 = divmod(r_y, 256)
        _values = [
            ord('a'), ord('t'),
            val_11, val_12,
            val_21, val_22,
            val_31, val_32,
            val_41, val_42,
            lb, rb,
            axis_b_l, axis_b_r,

            0, 0,

        ]
        i2c.write(_values)
