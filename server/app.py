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
from server.controller import Controller
from server.light import Light
from server.motor import Motor
from server.video import Video
from settings import JoyButtons

__version__ = '0.0.8'

print 'server', __version__


class Application(object):

    def __init__(self):
        self.logger = get_logger('server')

        gpio.init()

        self.serial_tty = serial.Serial(
            settings.TTY_ADDRESS,
            baudrate=settings.TTY_BAUDRATE,
            timeout=settings.TTY_TIMEOUT)

        self.motor_left = Motor("\xAA\x0A\x06", self.serial_tty, 'left', "\x0B", "\x0A", "\x09", "\x08", self.logger)
        self.motor_right = Motor("\xAA\x0A\x07", self.serial_tty, 'right', "\x0F", "\x0E", "\x0D", "\x0C", self.logger)
        self.light = Light(getattr(port, settings.LIGHT_PORT))
        self.video = Video()
        self.i2c_controller = Controller(settings.I2C_ADDRESS, settings.I2C_PORT)

        self.server = SocketServer.UDPServer((settings.SERVER_HOST, settings.SERVER_PORT), self.handle_request)
        self.server.timeout = settings.MOTOR_COMMAND_TIMEOUT

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sender.bind((settings.SOCKET_CLIENT_HOST, settings.SOCKET_CLIENT_PORT))

        self.is_running = False
        self.last_handle_request_time = 0

        self.last_light_value = 0
        self.last_light_value_time = time()

        self.last_video_value = 0
        self.last_video_value_time = time()

        # дата актуальности, данные телеметрии, температура, фото датчик
        self.telem_values = [0, 0, 0, 0]

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

    def _get_value(self, value):
        """
        преобразуем значение -1...+1 в значение от 0...65535
        """
        if value < -1:
            value = -1
        elif value > 1:
            value = 1

        try:
            value = int((65535 * (value + 1))/2)
        except ZeroDivisionError:
            value = 0

        return value

    def __process_light_value(self, value):
        """
        обработка включения/выключения фар
        """
        if value:
            if self.last_light_value == value:
                ct = time()
                if 6 > (ct - self.last_light_value_time) > 3:
                    self.light.toggle_state()
                    self.last_light_value_time = ct
            elif self.last_light_value == 0:
                self.last_light_value_time = time()
        self.last_light_value = value

    def __process_video_value(self, value):
        """
        обработка включения/выключения видео
        """
        if value:
            if self.last_video_value == value:
                ct = time()
                if 6 > (ct - self.last_video_value_time) > 3:
                    self.video.toggle_state()
                    self.last_video_value_time = ct
            elif self.last_video_value == 0:
                self.last_video_value_time = time()
        self.last_video_value = value

    def handle_buttons(self, values):
        """
        обработчик состояния кнопок
        """

        # обработаем включение/выключение фонарика
        self.__process_light_value(values[settings.LIGHT_KEY])
        # обработаем включение/выключение видео
        self.__process_video_value(values[settings.VIDEO_KEY])

        # отправим контроллеру значения для команд
        self.i2c_controller.write_values(
            self._get_value(values[JoyButtons.JOY_LT]),
            self._get_value(values[JoyButtons.JOY_RT]),
            self._get_value(values[JoyButtons.JOY_L_LR]),
            self._get_value(values[JoyButtons.JOY_L_UD]),
            255 if values[JoyButtons.JOY_LB] > 0 else 0,
            255 if values[JoyButtons.JOY_RB] > 0 else 0,
            255 if values[JoyButtons.JOY_B_AXIS_L] > 0 else 0,
            255 if values[JoyButtons.JOY_B_AXIS_R] > 0 else 0,
        )
        return [self.light.state, self.video.state]

    def handle_controller_values(self, values):
        """
        обработка остальных кнопок
        :param values:
        """

    def update_telem_values(self):
        """
        обновляем данные телеметрии
        """
        values = self.i2c_controller.read_values()

        if values:
            self.telem_values = values

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

            # обрабатываем кнопки
            values = self.handle_axis_motion(joy_state)
            values.extend(self.handle_buttons(joy_state))
            # обрабатываем остальные параметры
            self.handle_controller_values(joy_state)

            if (self.last_handle_request_time - self.telem_values[0]) > settings.TELEM_UPDATE_TIME:
                # обновляем данные телеметрии
                self.update_telem_values()

            values.extend(self.telem_values)

            self.sender.sendto(
                ','.join(str(i) for i in values),
                (client_address[0], settings.DASHBOARD_PORT)
            )

    def start(self):
        """"""
        self.logger.debug('start')
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
