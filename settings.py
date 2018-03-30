# coding: utf-8
# ilnurgi
# статик переменные

import json
import os

DIR_BASE = os.path.dirname(__file__)

settings_path = os.path.join(DIR_BASE, 'settings.json')
LOGS_PATH = os.path.join(DIR_BASE, 'logs')

# ======
# КЛИЕНТ
# ======

SOCKET_CLIENT_HOST = '0.0.0.0'
SOCKET_CLIENT_PORT = 0

# ======
# СЕРВЕР
# ======

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 0

# настройки устройства на сервере
TTY_ADDRESS = '/dev/ttyACM0'
TTY_BAUDRATE = 9600
TTY_TIMEOUT = 0.3

# время, через которое моторы остановятся, если нет команд
MOTOR_COMMAND_TIMEOUT = 1

# настройки панели состояния
DASHBOARD_REQUEST_TIMEOUT = 0.02  # чтобы интерфейс не тормозил
DASHBOARD_HOST = ''
DASHBOARD_PORT = 0


class JoyButtons:
    JOY_B_A = 0
    JOY_B_B = 1
    JOY_B_X = 2
    JOY_B_Y = 3
    JOY_LB = 4
    JOY_RB = 5
    JOY_B6 = 6
    JOY_B7 = 7
    JOY_B8 = 8
    JOY_B_AXIS_L = 9
    JOY_B_AXIS_R = 10

    JOY_L_LR = 11
    JOY_L_UD = 12
    JOY_LT = 13
    JOY_R_UD = 14
    JOY_R_LR = 15
    JOY_RT = 16

    BUTTONS = (
        JOY_B_A,
        JOY_B_B,
        JOY_B_X,
        JOY_B_Y,
        JOY_LB,
        JOY_RB,
        JOY_B6,
        JOY_B7,
        JOY_B8,
        JOY_B_AXIS_L,
        JOY_B_AXIS_R,
    )
    JOYS = (
        JOY_L_LR,
        JOY_L_UD,
        JOY_LT,
        JOY_R_UD,
        JOY_R_LR,
        JOY_RT,
    )
    JOY_COUNT_STATES = len(JOYS) + len(BUTTONS)


# фонарик
LIGHT_PORT = 'PG0'
LIGHT_KEY = JoyButtons.JOY_B_A

# включение видео
VIDEO_KEY = JoyButtons.JOY_B_B

# I2C
I2C_ADDRESS = '/dev/i2c-2'
I2C_PORT = 0x32
I2C_READ_BYTES_COUNT = 16

TELEM_UPDATE_TIME = 3

VIDEO_STREAM_CMD = (
    'cvlc v4l2:///dev/video0:chroma=h264:width=800:height=480:live-caching=50 '
    ':sout=#udp{dst=192.168.1.26:1234} :sout-keep')

VIDEO_SHOW_CMD = 'mplayer  udp://:1234'
USER_UID = 1000
USER_GID = 1000

if os.path.exists(settings_path):
    try:
        json_params = json.load(open(settings_path))
    except ValueError:
        pass
    else:
        globals().update(json_params)

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)