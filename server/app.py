# coding: utf-8
# ilnurgi
# приложение

import SocketServer
import socket

import time

try:
    import serial
except ImportError:
    import serial_fake as serial

import settings

from helpers import get_logger
from server.motor import Motor
from settings import JoyButtons

__version__ = '0.0.3'

print 'server version:', __version__


class Application(object):

    def __init__(self):
        self.logger = get_logger('server')
        self.serial_tty = serial.Serial(
            settings.TTY_ADDRESS,
            baudrate=settings.TTY_BAUDRATE,
            timeout=settings.TTY_TIMEOUT)

        self.motor_left = Motor("\xAA\x0A\x06", self.serial_tty, 'left', "\x0B", "\x0A", "\x09", "\x08", self.logger)
        self.motor_right = Motor("\xAA\x0A\x07", self.serial_tty, 'right', "\x0F", "\x0E", "\x0D", "\x0C", self.logger)

        self.server = SocketServer.UDPServer(('localhost', settings.BROADCAST_PORT), self.handle_request)
        self.server.timeout = settings.MOTOR_COMMAND_TIMEOUT

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sender.bind((settings.SENDER_HOST, settings.DASHBOARD_PORT))

        self.is_running = False
        self.last_handle_request_time = 0

    def motors_off(self):
        """
        выключаем все моторы
        """
        self.logger.debug('motors off')
        self.motor_left.off()
        self.motor_right.off()

    def handle_axis_motion(self, values, client_address):
        """
        обработчик событий 3х мерного джоя
        """
        left_value = int(values[JoyButtons.JOY_L_UD] * 255) + int(values[JoyButtons.JOY_L_LR] * 255)
        right_value = int(values[JoyButtons.JOY_L_UD] * 255) - int(values[JoyButtons.JOY_L_LR] * 255)
        self.motor_left.process_value(left_value)
        self.motor_right.process_value(right_value)
        print(left_value, right_value, client_address[0])
        self.sender.sendto('{0},{1}'.format(left_value, right_value), (client_address[0], settings.DASHBOARD_PORT))

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

        if len(joy_state) == JoyButtons.JOY_COUNT_STATES:
            self.handle_buttons(joy_state)
            self.handle_axis_motion(joy_state, client_address)

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
