"""
Добавление логов.
"""
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='WARNING',
           rotation='1 MB', compression='zip')
