# coding: utf-8
# ilnurgi
# статик переменные

import json

import os

settings_path = os.path.join(
    os.path.dirname(__file__),
    'settings.json'
)

SENDER_HOST = '0.0.0.0'
SENDER_PORT = 0

BROADCAST_HOST = '0.0.0.0'
BROADCAST_PORT = 0

if os.path.exists(settings_path):
    try:
        json_params = json.load(open(settings_path))
    except ValueError:
        pass
    else:
        globals().update(json_params)
