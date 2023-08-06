from rlogging import levels
from rlogging.records import Record
from rlogging.controllers import logging_controller


class BaseLogger(object):
    """Базовый класс логера, реализующий основной функционал."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def transfer(self, record: Record):
        logging_controller.push(record)

    def record(self, level, message: str, args: tuple, kwargs: dict) -> Record:
        assert isinstance(level, int)
        assert isinstance(message, str)
        assert isinstance(args, tuple)
        assert isinstance(kwargs, dict)

        record = Record(self.name, level, message, args, kwargs)

        self.transfer(record)

        return record


class Logger(BaseLogger):
    """Простой логер сообщений"""

    def log(self, level, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня level.

        Args:
            level (int): Уровень лога
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(level, message, args, kwargs)

    def debug(self, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня debug.

        Args:
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(levels.DEBUG_DEFAULT_LOGGING_LEVEL, message, args, kwargs)

    def info(self, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня info.

        Args:
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(levels.INFO_DEFAULT_LOGGING_LEVEL, message, args, kwargs)

    def warning(self, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня warning.

        Args:
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(levels.WARNING_DEFAULT_LOGGING_LEVEL, message, args, kwargs)

    def error(self, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня error.

        Args:
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(levels.ERROR_DEFAULT_LOGGING_LEVEL, message, args, kwargs)

    def critical(self, message: str, *args, **kwargs) -> Record:
        """Создать лог уровня critical.

        Args:
            message (str): Сообщение лога
            args (tuple): Доп параметры
            kwargs (dict): Доп параметры

        Returns:
            Record: Объект лога

        """

        return self.record(levels.CRITICAL_DEFAULT_LOGGING_LEVEL, message, args, kwargs)

    def exception(self, exception: Exception, *args, **kwargs) -> Record:
        """Создание лога на основе исключения

        Args:
            exception (Exception): Исключение

        """

        message = '{0}: {1}'.format(exception.__class__.__name__, exception)

        return self.record(levels.CRITICAL_DEFAULT_LOGGING_LEVEL, message, args, kwargs)


class GetLogger(object):
    """Интерфейс для получения создания и получения"""

    loggers: dict[str, Logger]

    def __init__(self) -> None:
        self.loggers = {}

    def __call__(self, logger_name: str) -> Logger:
        if logger_name not in self.loggers:
            self.loggers[logger_name] = Logger(logger_name)

        return self.loggers[logger_name]


get_logger = GetLogger()
