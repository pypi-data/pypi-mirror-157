"""Модуль гибкого логирования"""

from rlogging.controllers import set_handlers  # noqa: F401
from rlogging.handlers import Handler  # noqa: F401
from rlogging.loggers import get_logger
from rlogging.records import Record  # noqa: F401

__version__ = '0.4.1'


logger = get_logger('main')
