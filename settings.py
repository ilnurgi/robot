# coding: utf-8
# ilnurgi
# статик переменные

import json
import os

DIR_BASE = os.path.dirname(__file__)

settings_path = os.path.join(DIR_BASE, 'settings.json')
LOGS_PATH = os.path.join(DIR_BASE, 'logs')

# настройки клиента
SENDER_HOST = '0.0.0.0'
SENDER_PORT = 0

BROADCAST_HOST = '0.0.0.0'
BROADCAST_PORT = 0

# настройки устройства на сервере
TTY_ADDRESS = ''
TTY_BAUDRATE = 9600
TTY_TIMEOUT = 0.3

# время, через которое моторы остановятся, если нет команд
MOTOR_COMMAND_TIMEOUT = 1

# настройки панели состояния
DASHBOARD_REQUEST_TIMEOUT = 0.02  # чтобы интерфейс не тормозил
DASHBOARD_PORT = 0

class JoyButtons:
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

    BUTTONS = (
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
    )
    JOYS = (
        JOY_L_LR,
        JOY_L_UD,
        JOY_L_RT,
        JOY_R_UD,
        JOY_R_LR,
        JOY_R_RT,
    )
    JOY_COUNT_STATES = len(JOYS) + len(BUTTONS)

# фонарик
LIGHT_PORT = 'PG0'
LIGHT_KEY = JoyButtons.JOY_B0





if os.path.exists(settings_path):
    try:
        json_params = json.load(open(settings_path))
    except ValueError:
        pass
    else:
        globals().update(json_params)

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)