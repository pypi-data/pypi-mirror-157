from multiprocessing import Queue, current_process
from multiprocessing.managers import ValueProxy
from typing import Any, Iterable

from rlogging import processes
from rlogging.handlers import Handler
from rlogging.records import Record
from rlogging.superstructure.handlers import ConsoleHandler


class LoggingWorker(processes.SubProcessWorker):
    """Воркер контроллер передачи логов из логгеров в хендлеры"""

    def __init__(self, on_while: ValueProxy[bool], queue: Queue, handlers: list[Handler]):
        super().__init__(on_while, queue)
        self.handlers = handlers

    def init(self):
        for handler_instance in self.handlers:
            handler_instance.init()

    def processing_record(self, record: Record):
        for handler_instance in self.handlers:
            handler_instance.processing(record)

    def processing(self):
        for record in self.queue_entities:
            self.processing_record(record)


class LoggingController(processes.SubProcessController):
    """Контроллер модуля rlogging"""

    worker_class = LoggingWorker

    handlers: tuple[Handler]
    handlers_hash: int | None

    def __init__(self) -> None:
        super().__init__()

        self.handlers = []
        self.handlers_hash = None

    def make_worker(self) -> worker_class:
        return self.worker_class(self.on_while, self.queue, self.handlers)

    def push(self, entity: Any):
        """Передача в воркер некого объекта

        Args:
            entity (Any): Объект для передачи

        """

        self.queue.put(entity)

    def apply(self, handlers: Iterable[Handler]):
        # Ожидание, пока логи, сделанные при предыдущих настроек, обработаются
        if self.handlers_hash is not None:
            self.stop()

        self.handlers = tuple(handlers)
        self.handlers_hash = hash(self.handlers)

        self.start()


logging_controller = LoggingController()


def _handler_settings_check(handler_instance: Handler):
    return isinstance(handler_instance, Handler)


def set_handlers(*handlers: Handler):  # noqa: FNE008
    handlers = tuple(filter(_handler_settings_check, handlers))
    logging_controller.apply(handlers)


if current_process().name == 'MainProcess':
    set_handlers(ConsoleHandler())
