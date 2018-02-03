# coding: utf-8
# ilnurgi
# приложение

import SocketServer
import socket

from time import time

try:
    import serial
except ImportError:
    import serial_fake as serial

try:
    from pyA20.gpio import gpio
    from pyA20.gpio import port
except ImportError:
    from pyA20_fake import gpio, port

import settings

from helpers import get_logger
from server.light import Light
from server.motor import Motor
from settings import JoyButtons

__version__ = '0.0.5'

print 'server', __version__


class Application(object):

    def __init__(self):
        self.logger = get_logger('server')
        self.serial_tty = serial.Serial(
            settings.TTY_ADDRESS,
            baudrate=settings.TTY_BAUDRATE,
            timeout=settings.TTY_TIMEOUT)

        self.motor_left = Motor("\xAA\x0A\x06", self.serial_tty, 'left', "\x0B", "\x0A", "\x09", "\x08", self.logger)
        self.motor_right = Motor("\xAA\x0A\x07", self.serial_tty, 'right', "\x0F", "\x0E", "\x0D", "\x0C", self.logger)
        self.light = Light(getattr(gpio, settings.LIGHT_PORT))

        self.server = SocketServer.UDPServer(('', settings.BROADCAST_PORT), self.handle_request)
        self.server.timeout = settings.MOTOR_COMMAND_TIMEOUT

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sender.bind((settings.SENDER_HOST, settings.DASHBOARD_PORT))

        self.is_running = False
        self.last_handle_request_time = 0

        self.last_light_value = 0
        self.last_light_value_time = time()

    def motors_off(self):
        """
        выключаем все моторы
        """
        self.logger.debug('motors off')
        self.motor_left.off()
        self.motor_right.off()

    def handle_axis_motion(self, values):
        """
        обработчик событий 3х мерного джоя
        """
        left_value = int(values[JoyButtons.JOY_L_UD] * 255) + int(values[JoyButtons.JOY_L_LR] * 255)
        right_value = int(values[JoyButtons.JOY_L_UD] * 255) - int(values[JoyButtons.JOY_L_LR] * 255)
        self.motor_left.process_value(left_value)
        self.motor_right.process_value(right_value)
        return [left_value, right_value]

    def handle_buttons(self, values):
        """
        обработчик состояния кнопок
        """
        light_value = values[settings.LIGHT_KEY]

        if light_value == 1:
            if self.last_light_value == light_value:
                if time() - self.last_light_value_time > 3:
                    self.light.toggle_state()
            elif self.last_light_value == 0:
                self.last_light_value_time = time()

        self.last_light_value = light_value
        return [self.light.state]

    def handle_request(self, request, client_address, server):
        """
        обрабатывает запрос
        :param request: запрос
        :param client_address: адрес клиента
        :param server: сервер
        """

        self.last_handle_request_time = time()

        _request, _socket = request

        if ',' not in _request:
            return

        try:
            joy_state = [float(i) if '.' in i else int(i) for i in _request.split(',')]
        except (ValueError, TypeError):
            return

        if len(joy_state) == JoyButtons.JOY_COUNT_STATES:
            values = self.handle_axis_motion(joy_state)
            values.extend(self.handle_buttons(joy_state))
            self.sender.sendto(
                ','.join(str(i) for i in values),
                (client_address[0], settings.DASHBOARD_PORT)
            )

    def start(self):
        """"""
        self.logger.debug('start')
        gpio.init()
        self.motors_off()

        self.is_running = True
        self.last_handle_request_time = time()

        while self.is_running:
            if (time() - self.last_handle_request_time) > settings.MOTOR_COMMAND_TIMEOUT:
                self.last_handle_request_time = time()
                self.motors_off()

            # проверка пока приходит телеметрия
            self.server.handle_request()

        print 'Finished'
        self.motors_off()

        raw_input('Выключите питание, нажмите клавишу ВВОД, чтобы продолжить')

    def run(self):
        """
        запускаем приложение
        """
        try:
            self.start()
        except KeyboardInterrupt:
            self.motors_off()
            raw_input('Выключите питание, нажмите клавишу ВВОД, чтобы продолжить')
            self.motors_off()
        except Exception as err:
            self.logger.debug(err)
            import traceback
            self.logger.debug(traceback.format_exc())


if __name__ == '__main__':
    Application().run()
