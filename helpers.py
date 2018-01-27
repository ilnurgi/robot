# coding: utf-8
# ilnurgi
# вспомогательные методы

import logging
import os
import time

import settings


def get_logger(name):
    """
    возвращает логер
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    fh = logging.FileHandler(
        os.path.join(settings.LOGS_PATH, '{0}_{1}.log'.format(name, time.time())),
        mode='a',
        encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return logger
