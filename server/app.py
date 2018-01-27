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

__version__ = '0.0.1'

print 'server version:', __version__

# кнопка вниз
JOYBUTTONDOWN = 10
# кнопка вверх
JOYBUTTONUP = 11
# 3х мерный джой
JOYAXISMOTION = 7
# стрелка
JOYHATMOTION = 9

# левый вверх вниз
AXIS_L_Y = 1
# левый влево вправо
AXIS_L_X = 0
# левый по высоте
AXIS_L_Z = 2

# аналогично правый
AXIS_R_Y = 4
AXIS_R_X = 3
AXIS_R_Z = 5

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

        self.event_handlers = {
            JOYAXISMOTION: self.handle_axis_motion,
            JOYHATMOTION: self.handle_hat_motion,
            JOYBUTTONDOWN: self.handle_button_down,
            JOYBUTTONUP: self.handle_button_up,
        }

    def motors_off(self):
        """
        выключаем все моторы
        """
        self.logger.debug('motors off')
        self.motor_left.off()
        self.motor_right.off()

    def handle_axis_motion(self, event_type, axis, value):
        """
        обработчик событий 3х мерного джоя
        """
        print 'handle_axis_motion', event_type, axis, value

        if axis == AXIS_L_Y:
            # левый мотор вперед
            self.motor_left.process_value(value)
        elif axis == AXIS_R_Y:
            # левый мотор вперед
            self.motor_right.process_value(value)

    def handle_hat_motion(self, event_type, hat, value_0, value_2):
        """
        обработчик крестика
        """
        print 'handle_hat_motion', event_type, hat, value_0, value_2

    def handle_button_down(self, event_type, button):
        """
        обработчик нажатия кнопки
        """
        print 'handle_button_down', event_type, button

    def handle_button_up(self, event_type, button):
        """
        обработчик отпускания кнопки
        """
        print 'handle_button_up', event_type, button

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
            params = [float(i) if '.' in i else int(i) for i in _request.split(',')]
        except (ValueError, TypeError):
            return

        if params[0] in self.event_handlers:
            self.event_handlers[params[0]](*params)

        # # Separate the command into individual drives
        # driveCommands = request.split(',')
        #
        # if len(driveCommands) == 1:
        #     # Special commands
        #     if request == 'ALLOFF':
        #         # Turn all drives off
        #         logger.debug('command ALLOFF')
        #         all_motor_off()
        #     elif request == 'EXIT':
        #         logger.debug('command EXIT')
        #         # Exit the program
        #         IS_RUNNING = False
        #     else:
        #         logger.debug('Special command "%s" not recognised' % (request))
        #         # Unknown command
        #         print 'Special command "%s" not recognised' % (request)
        #
        # elif len(driveCommands) == 16:
        #     # 16 - длинна принятого массива команд
        #     motor_left.process_value(
        #         int(driveCommands[0]) + int(driveCommands[1]))
        #     motor_right.process_value(
        #         int(driveCommands[0]) - int(driveCommands[1]))
        # else:
        #     logger.debug('Command "%s" did not have parts!' % (request))
        #     # Did not get the right number of drive commands
        #     print 'Command "%s" did not have parts!' % (request)

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
