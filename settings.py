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

if os.path.exists(settings_path):
    try:
        json_params = json.load(open(settings_path))
    except ValueError:
        pass
    else:
        globals().update(json_params)

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)
