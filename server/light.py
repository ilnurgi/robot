# coding: utf-8
"""
модуль управления фонариком
"""

try:
    from pyA20.gpio import gpio
    from pyA20.gpio import port
except ImportError:
    from pyA20_fake import gpio, port

ON = 1
OFF = 0


class Light(object):

    def __init__(self, port):
        """
        инициализация объекта
        """
        self.port = port
        self.state = gpio.LOW

        gpio.setcfg(self.port, gpio.OUTPUT)
        gpio.pullup(self.port, gpio.PULLDOWN)

        self.off()

    def on(self):
        """
        включает устройство
        """
        if self.state == ON:
            return

        gpio.output(self.port, gpio.HIGH)
        self.state = ON

    def off(self):
        """
        выключает устройство
        """
        if self.state == OFF:
            return

        gpio.output(self.port, gpio.LOW)
        self.state = OFF

    def toggle_state(self):
        """
        меняет свое состояние
        """
        if self.state == OFF:
            self.on()
        else:
            self.off()
