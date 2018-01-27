# coding: utf-8
# ilnurgi
# клиентская часть для робота, проксирует геймпад на работа

import socket
import time

import pygame
import pygame.event
import pygame.joystick

import settings

__version__ = '0.0.4'

print 'gamepad proxy:', __version__

# кнопка вниз
JOYBUTTONDOWN = pygame.JOYBUTTONDOWN
# кнопка вверх
JOYBUTTONUP = pygame.JOYBUTTONUP
# 3х мерный джой
JOYAXISMOTION = pygame.JOYAXISMOTION
# стрелка
JOYHATMOTION = pygame.JOYHATMOTION

QUIT = pygame.QUIT

# значения состояний кнопок
JOY_STATE = []


def process_events(events, num_buttons):
    """
    обработка событий
    :param events: список событий
    """
    for event in events:
        if event.type == JOYAXISMOTION:
            JOY_STATE[num_buttons + event.axis] = event.value
        elif event.type == JOYBUTTONUP or event.type == JOYBUTTONDOWN:
            JOY_STATE[event.button] = int(event.type == JOYBUTTONDOWN)
        elif event.type == QUIT:
            return False
    return True

def run():

    pygame.init()
    if not pygame.joystick.get_count():
        print 'ERROR: joystick count is 0'
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    joystick_num_buttons = joystick.get_numbuttons()
    joystick_num_axes = joystick.get_numaxes()

    print 'joystick found:', joystick.get_name()
    print 'count buttons:', joystick_num_buttons
    print 'count axes:', joystick_num_axes

    # кнопки
    JOY_STATE.extend([0 for _ in range(joystick_num_buttons)])
    # ползунки
    JOY_STATE.extend([0.0 for _ in range(joystick_num_axes)])

    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sender.bind((settings.SENDER_HOST, settings.SENDER_PORT))

    # нам нужны только события джойстика
    pygame.event.set_allowed([JOYAXISMOTION, JOYBUTTONUP, JOYBUTTONDOWN, QUIT])

    get = pygame.event.get
    sleep = time.sleep

    send_to = sender.sendto
    BROADCAST_HOST = settings.BROADCAST_HOST
    BROADCAST_PORT = settings.BROADCAST_PORT

    while True:
        # бесконечный сбор событий с геймпада
        if process_events(get(), joystick_num_buttons):
            send_to(','.join(str(i) for i in JOY_STATE), (BROADCAST_HOST, BROADCAST_PORT))
        else:
            break
        sleep(0.1)


if __name__ == '__main__':
    run()
