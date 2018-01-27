# coding: utf-8
# ilnurgi
# приложение

import SocketServer

import time

try:
    import serial
except ImportError:
    import serial_fake as serial

import settings

from helpers import get_logger
from server.motor import Motor

__version__ = '0.0.3'

print 'server version:', __version__

JOY_B0 = 0
JOY_B1 = 1
JOY_B2 = 2
JOY_B3 = 3
JOY_B4 = 4
JOY_B5 = 5
JOY_B6 = 6
JOY_B7 = 7
JOY_B8 = 8
JOY_B9 = 9
JOY_B10 = 10

JOY_L_LR = 11
JOY_L_UD = 12
JOY_L_RT = 13
JOY_R_UD = 14
JOY_R_LR = 15
JOY_R_RT = 16

JOYS = (
    JOY_B0,
    JOY_B1,
    JOY_B2,
    JOY_B3,
    JOY_B4,
    JOY_B5,
    JOY_B6,
    JOY_B7,
    JOY_B8,
    JOY_B9,
    JOY_B10,
    JOY_L_LR,
    JOY_L_UD,
    JOY_L_RT,
    JOY_R_UD,
    JOY_R_LR,
    JOY_R_RT,
)
JOY_COUNT_STATES = len(JOYS)


class Application(object):

    def __init__(self):
        self.logger = get_logger('server')
        self.serial_tty = serial.Serial(
            settings.TTY_ADDRESS,
            baudrate=settings.TTY_BAUDRATE,
            timeout=settings.TTY_TIMEOUT)

        self.motor_left = Motor("\xAA\x0A\x06", self.serial_tty, 'left', "\x0B", "\x0A", "\x09", "\x08", self.logger)
        self.motor_right = Motor("\xAA\x0A\x07", self.serial_tty, 'right', "\x0F", "\x0E", "\x0D", "\x0C", self.logger)

        self.remote_server = SocketServer.UDPServer(('', settings.BROADCAST_PORT), self.handle_request)
        self.remote_server.timeout = settings.MOTOR_COMMAND_TIMEOUT
        
        self.is_running = False
        self.last_handle_request_time = 0

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
        self.motor_left.process_value(
            int(values[JOY_L_UD] * 255) + int(values[JOY_L_LR] * 255))
        self.motor_right.process_value(
            int(values[JOY_L_UD] * 255) - int(values[JOY_L_LR] * 255))

    def handle_buttons(self, values):
        """
        обработчик состояния кнопок
        """

    def handle_request(self, request, client_address, server):
        """
        обрабатывает запрос
        :param request: запрос
        :param client_address: адрес клиента
        :param server: сервер
        """

        self.last_handle_request_time = time.time()

        _request, _socket = request

        if ',' not in _request:
            return

        try:
            joy_state = [float(i) if '.' in i else int(i) for i in _request.split(',')]
        except (ValueError, TypeError):
            return

        if len(joy_state) == JOY_COUNT_STATES:
            self.handle_buttons(joy_state)
            self.handle_axis_motion(joy_state)

    def start(self):
        """"""
        self.logger.debug('start')
        self.motors_off()

        self.is_running = True
        self.last_handle_request_time = time.time()

        while self.is_running:
            if (time.time() - self.last_handle_request_time) > settings.MOTOR_COMMAND_TIMEOUT:
                self.last_handle_request_time = time.time()
                self.motors_off()

            # проверка пока приходит телеметрия
            self.remote_server.handle_request()

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
