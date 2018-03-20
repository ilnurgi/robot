# coding: utf-8

"""
видео проигрыватель
"""

import subprocess
import settings

ON = 1
OFF = 0


class Video(object):

    def __init__(self):
        """
        инициализация объекта
        """
        self.process = None
        self.state = OFF

    def on(self):
        """
        включает видео
        """
        if self.state == ON:
            return

        self.process = subprocess.Popen(settings.VIDEO_STREAM_CMD, shell=True)
        self.state = ON

    def off(self):
        """
        выключает видео
        """
        if self.state == OFF:
            return

        self.process.terminate()
        self.state = OFF

    def toggle_state(self):
        """
        меняет свое состояние
        """
        if self.state == OFF:
            self.on()
        else:
            self.off()
