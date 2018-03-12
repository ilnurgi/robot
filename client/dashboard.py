# coding: utf-8

"""
панель управления роботом
"""

import SocketServer

from datetime import datetime

from Tkinter import Tk, LabelFrame, Scale, Label

import settings

from helpers import get_logger

__version__ = '0.0.6'

print 'dashboard', __version__

after_timeout = int(settings.DASHBOARD_REQUEST_TIMEOUT * 1000)


class Application(object):

    def __init__(self):
        self.logger = get_logger('dashboard')

        self.server = SocketServer.UDPServer((settings.DASHBOARD_HOST, settings.DASHBOARD_PORT), self.handle_request)
        self.server.timeout = settings.DASHBOARD_REQUEST_TIMEOUT

        self.init_layout()

    def init_layout(self):
        self.window = Tk()
        self.window.wm_minsize(400, 400)

        self.w_lf_motor = LabelFrame(self.window, text=u'Моторы')
        self.w_scale_motor1 = Scale(self.w_lf_motor, from_=-255, to=255)
        self.w_scale_motor2 = Scale(self.w_lf_motor, from_=-255, to=255)

        self.w_lf_light = LabelFrame(self.window, text=u'Свет')
        self.w_l_light = Label(self.w_lf_light, text=u'Выключен', fg='red', font='Arial 20')

        self.w_lf_telem = LabelFrame(self.window, text=u'Телеметрия')
        self.w_l_telem_time = Label(self.w_lf_telem, text=u'0', font='Arial 15')
        self.w_l_telem_bat = Label(self.w_lf_telem, text=u'0', font='Arial 15')
        self.w_l_telem_temp = Label(self.w_lf_telem, text=u'0', font='Arial 15')
        self.w_l_telem_photo = Label(self.w_lf_telem, text=u'0', font='Arial 15')

        self.w_lf_motor.place(relx=0, rely=0, relwidth=1, relheight=0.3)
        self.w_scale_motor1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.w_scale_motor2.place(relx=0.5, rely=0, relwidth=1, relheight=1)

        self.w_lf_light.place(relx=0, rely=0.3, relwidth=1, relheight=0.3)
        self.w_l_light.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.w_lf_telem.place(relx=0, rely=0.6, relwidth=1, relheight=0.4)
        Label(self.w_lf_telem, text=u'Время:', font='Arial 15').place(relx=0, rely=0, relwidth=0.5, relheight=0.25)
        Label(self.w_lf_telem, text=u'Батарея:', font='Arial 15').place(relx=0, rely=0.25, relwidth=0.5, relheight=0.25)
        Label(self.w_lf_telem, text=u'Температура:', font='Arial 15').place(relx=0, rely=0.5, relwidth=0.5, relheight=0.25)
        Label(self.w_lf_telem, text=u'Свет:', font='Arial 15').place(relx=0, rely=0.75, relwidth=0.5, relheight=0.25)
        self.w_l_telem_time.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.25)
        self.w_l_telem_bat.place(relx=0.5, rely=0.25, relwidth=0.5, relheight=0.25)
        self.w_l_telem_temp.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.25)
        self.w_l_telem_photo.place(relx=0.5, rely=0.75, relwidth=0.5, relheight=0.25)

        self.raw_telem_time = 0
        self.raw_telem_bat = 0
        self.raw_telem_temp = 0
        self.raw_telem_photo = 0

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
        """
        устанавливает значение для фонарика
        :param value:
        """
        if value == 1:
            self.w_l_light['text'] = u'Включен'
            self.w_l_light['fg'] = 'green'
        else:
            self.w_l_light['text'] = u'Выключен'
            self.w_l_light['fg'] = 'red'

    def set_time(self, value):
        """
        устанавливает значение для даты
        :param value:
        """
        if self.raw_telem_time == value:
            return
        self.raw_telem_time = value

        try:
            value = datetime.fromtimestamp(value).strftime('%Y.%m.%d %H:%M:%S')
        except Exception as err:
            print(err)
            self.logger.debug(str(err))

        self.w_l_telem_time['text'] = value

    def set_bat(self, value):
        """
        устанавливает значение для батареи
        :param value:
        """
        if self.raw_telem_bat == value:
            return
        self.raw_telem_bat = value

        self.w_l_telem_bat['text'] = value

    def set_temp(self, value):
        """
        устанавливает значение для температуры
        :param value:
        """
        if self.raw_telem_temp == value:
            return
        self.raw_telem_temp = value

        offset = -0.01
        t_sensor = ((value * (1.1 / 1024.0)) - 0.5 + offset) * 100
        error = 244e-6 * (125 - t_sensor) * (t_sensor - -40.0) + 2E-12 * (t_sensor - -40.0) - 2.0
        temp = t_sensor - error

        temp2 = (value*5/1024.0 - 0.5)/0.01
        if 20 >= temp2 <= 25:
            temp2 = value*3.3/1024.0

        self.w_l_telem_temp['text'] = '{0}/{1} ({2})'.format(round(temp, 3), round(temp2, 3), value)

    def set_photo(self, value):
        """
        устанавливает значение для температуры
        :param value:
        """
        if self.raw_telem_photo == value:
            return
        self.raw_telem_photo = value

        self.w_l_telem_photo['text'] = value

    def handle_request(self, request, client_address, server):
        """
        обработка входных данных
        :param request:
        :param client_address:
        :param server:
        :return:
        """
        _request, _socket = request

        if ',' not in _request:
            return

        values = [int(i) for i in _request.split(',')]

        self.set_motor_value(*values[:2])
        self.set_light(values[2])
        self.set_time(values[3])
        self.set_temp(values[4])
        self.set_bat(values[5])
        self.set_photo(values[6])

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