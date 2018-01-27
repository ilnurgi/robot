# coding: utf-8
# ilnurgi
# клиентская часть для робота, проксирует геймпад на работа

import socket

import pygame
import pygame.event
import pygame.joystick

import settings

__version__ = '0.0.1'

def process_event(event):
    """
    обработка события, возвращаем результат обработкаи
    :param event: событие
    """
    result = None

    if event.type == JOYAXISMOTION:
        result = '{event.type},{event.axis},{event.value}'.format(event=event)
    elif event.type == JOYHATMOTION:
        result = '{event.type},{event.hat},{event.value[0]},{event.value[1]}'.format(event=event)
    elif event.type == JOYBUTTONUP or event.type == JOYBUTTONDOWN:
        result = '{event.type},{event.button}'.format(event=event)

    return result

# кнопка вниз
JOYBUTTONDOWN = pygame.JOYBUTTONDOWN
# кнопка вверх
JOYBUTTONUP = pygame.JOYBUTTONUP
# 3х мерный джой
JOYAXISMOTION = pygame.JOYAXISMOTION
# стрелка
JOYHATMOTION = pygame.JOYHATMOTION

pygame.init()
if not pygame.joystick.get_count():
    print 'ERROR: joystick count is 0'
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print 'joystick found:', joystick.get_name()

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sender.bind((settings.SENDER_HOST, settings.SENDER_PORT))

# нам нужны только события джойстика
pygame.event.set_allowed([JOYHATMOTION, JOYAXISMOTION, JOYBUTTONUP, JOYBUTTONDOWN])

wait = pygame.event.wait
send_to = sender.send
BROADCAST_HOST = settings.BROADCAST_HOST
BROADCAST_PORT = settings.BROADCAST_PORT

while True:
    # бесконечный сбор событий с геймпада
    result = process_event(wait())
    if result is not None:
        sender.sendto(result, (BROADCAST_HOST, BROADCAST_PORT))
