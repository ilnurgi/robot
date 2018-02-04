# coding: utf-8

"""
панель управления роботом
"""

import SocketServer

from Tkinter import Tk, LabelFrame, Scale, Label

import settings

from helpers import get_logger
from settings import JoyButtons

__version__ = '0.0.4'

print 'dashboard', __version__

after_timeout = int(settings.DASHBOARD_REQUEST_TIMEOUT * 1000)


class Application(object):

    def __init__(self):
        self.logger = get_logger('dashboard')

        self.server = SocketServer.UDPServer(('localhost', settings.DASHBOARD_PORT), self.handle_request)
        self.server.timeout = settings.DASHBOARD_REQUEST_TIMEOUT

        self.init_layout()

    def init_layout(self):
        self.window = Tk()

        self.w_lf_motor = LabelFrame(self.window, text=u'Моторы')
        self.w_scale_motor1 = Scale(self.w_lf_motor, from_=-255, to=255)
        self.w_scale_motor2 = Scale(self.w_lf_motor, from_=-255, to=255)

        self.w_lf_light = LabelFrame(self.window, text=u'Свет')
        self.w_l_light = Label(self.w_lf_light, text=u'Выключен', fg='red', font='Arial 20')

        self.w_lf_motor.place(relx=0, rely=0, relwidth=1, relheight=0.5)
        self.w_scale_motor1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.w_scale_motor2.place(relx=0.5, rely=0, relwidth=1, relheight=1)

        self.w_lf_light.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)
        self.w_l_light.place(relx=0, rely=0, relwidth=1, relheight=1)

    def set_motor_value(self, left_value, right_value):
        if left_value > 255:
            left_value = 255
        elif left_value < -255:
            left_value = -255
        self.w_scale_motor1.set(left_value)

        if right_value > 255:
            right_value = 255
        elif right_value < -255:
            right_value = -255
        self.w_scale_motor2.set(right_value)

    def set_light(self, value):
        """"""
        if value == 1:
            self.w_l_light['text'] = u'Включен'
            self.w_l_light['fg'] = 'green'
        else:
            self.w_l_light['text'] = u'Выключен'
            self.w_l_light['fg'] = 'red'

    def handle_request(self, request, client_address, server):
        """
        обработка входных данных
        :param request:
        :param client_address:
        :param server:
        :return:
        """
        _request, _socket = request
        print _request
        if ',' not in _request:
            return

        values = [int(i) for i in _request.split(',')]
        self.set_motor_value(*values[:2])
        self.set_light(values[2])

    def wait_request(self):
        """"""
        self.server.handle_request()
        self.register_mainloop()

    def register_mainloop(self):
        """
        регистриуем обработчик, который периодический будет обрабатывать события
        """
        self.window.after(after_timeout, self.wait_request)

    def run(self):
        """"""
        try:
            self.register_mainloop()
            self.window.mainloop()
        except KeyboardInterrupt:
            pass
        except Exception as err:
            self.logger.debug(err)
            import traceback
            self.logger.debug(traceback.format_exc())
            raise

Application().run()