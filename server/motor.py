# coding: utf-8
# ilnurgi
# класс для работы с мотором

# мотор выключен
OFF = 0
# мотор включен
MOVE = 1
# мотор остановлен
STOP = 2


class Motor:

    def __init__(self, idi, serial_tty, name, b1, b2, f1, f2, logger):
        print 'init motor', name

        # идентификатор мотора
        self.id = idi

        # адрес tty устройства
        self.serial = serial_tty

        # просто название мотора
        self.name = name

        # какие то пины видимо
        self.b1 = b1
        self.b2 = b2
        self.f1 = f1
        self.f2 = f2

        self.logger = logger

        # состояние мотора
        self.state = OFF

    def off(self):
        """
        выключает мотор
        """
        if self.state == OFF:
            return

        self.debug('off')
        self.serial.write(self.id + "\x00")

    def backward(self, value):
        """
        движение назад
        """
        self.debug('backward', value)

        value = abs(value)
        if value > 127:
            self.serial.write("\xAA\x0A" + self.b1 + chr(value-128))
        else:
            self.serial.write("\xAA\x0A" + self.b2 + chr(value))
        self.state = MOVE

    def forward(self, value):
        """
        движение вперед
        """
        self.debug('forward', value)

        if value > 127:
            self.serial.write ("\xAA\x0A" + self.f1 + chr(value-128))
        else:
            self.serial.write ("\xAA\x0A" + self.f2 + chr(value))
        self.state = MOVE

    def stop(self, value):
        """
        остановка
        """
        if self.state == STOP:
            return

        self.debug('stop', value)
        self.serial.write(self.id + "\x00")

    def process_value(self, value):
        """
        обработка значения
        """
        if value > 255 :
            value = 255
        elif value < -255:
            value = -255

        if -256 < value < -15:
            self.backward(value)
        elif 15 < value < 256:
            self.forward(value)
        else:
            self.stop(value)

    def debug(self, *args):
        self.logger.debug('motor: {0}, {1}'.format(self.name, *args))
