from __future__ import annotations

import inspect
from multiprocessing import current_process
import os
import threading
import time
from itertools import chain
from typing import Any

from rlogging import levels


def record_dev_dump(record: Record):
    print('Dev dumb record instance:')
    print(f'| now pid_id: {os.getpid()}')
    print(f'| now thread_id: {threading.get_ident()}')
    print(f'| | self id: {id(record)}')
    print(f'| | record message: {record.message}')
    print(f'| | record pid_id: {record.pid_id} / {record.pid_id == os.getpid()}')
    print(f'| | record thread_id: {record.thread_id} / {record.thread_id == threading.get_ident()}')


def get_logging_level_label(level: int) -> str:
    for max_score_for_level, level_label in levels.LOGGING_LEVELS.items():
        if max_score_for_level >= level:
            return level_label


def get_object_from_stack(stack: inspect.FrameInfo) -> str:  # noqa: FNE008
    """Получение строковой ссылки до объекта, из которого был создан лог

    Args:
        stack (FrameInfo): FrameInfo

    Returns:
        str: Объект, из которого был создан лог

    """

    parent_function_object_name = ''
    function_name = '' if stack.function == '<module>' else stack.function

    if some_object := stack.frame.f_locals.get('self'):
        parent_function_object_name = some_object.__class__.__name__

    elif some_class := stack.frame.f_locals.get('cls'):

        if isinstance(some_class, type):
            parent_function_object_name = some_class.__name__

        else:
            parent_function_object_name = some_class.__class__.__name__

    return f'{parent_function_object_name}.{function_name}'.strip('.')


class Record(object):
    """Класс записи лога"""

    __slots__ = (
        'logger_name',
        'level',
        'message',
        'args',
        'kwargs',
        'timestamp',
        'pid_id',
        'process_name',
        'thread_id',
        'from_file',
        'from_file_line',
        'from_module',
        'from_object',
        'level_label',
        'level_label_center',
    )

    # Поля из вне
    logger_name: str
    level: int
    message: str
    kwargs: dict[str, str]

    # Поле определившиеся при инициализации
    timestamp: float
    pid_id: int
    process_name: str
    thread_id: int

    # Инспектируемая информация
    from_file: str
    from_file_line: str
    from_module: str
    from_object: str | None

    # Параметры с отложенной генерацией
    level_label: str | None
    level_label_center: str | None

    @classmethod
    @property
    def __all_slots__(cls) -> list:
        """Получение списка всех доступных параметров, основном на переменной __slot__

        Returns:
            list: Список доступных параметров

        """

        return list(chain.from_iterable(getattr(sub_class, '__slots__', []) for sub_class in cls.__mro__))

    @property
    def __dict__(self) -> dict:
        return {attr: getattr(self, attr) for attr in self.__all_slots__}

    def __dd__(self):
        record_dev_dump(self)

    def __init__(self, logger_name: str, level: int, message: str, args: tuple[Any], kwargs: dict[str, str]) -> None:
        self.logger_name = logger_name
        self.level = level
        self.message = message
        self.args = args
        self.kwargs = kwargs

        self._gen_fields()

    def _gen_fields(self):
        self.timestamp = time.time()
        self.pid_id = os.getpid()
        self.process_name = current_process().name
        self.thread_id = threading.get_ident()

        # на 5 уровня вверх от данной функции (определяется экспериментальным путем)
        stack = inspect.stack()[4]
        module = inspect.getmodule(stack.frame)

        self.from_file = stack.filename
        self.from_file_line = stack.lineno

        self.from_module = module.__name__
        self.from_object = get_object_from_stack(stack)

        self.level_label = get_logging_level_label(self.level)
        self.level_label_center = self.level_label.center(8)
