from multiprocessing import Queue, Process
from multiprocessing.managers import ValueProxy
from time import sleep
from typing import Iterable
from execution_controller.processes import start_tracking


class SubProcessWorker(object):
    """Воркер, обрабатывающий логи в своем процессе"""

    queue: Queue
    on_while: ValueProxy[bool]

    def __init__(self, on_while: ValueProxy[bool], queue: Queue):
        self.on_while = on_while
        self.queue = queue

    @property
    def queue_entities(self) -> Iterable:
        while not self.queue.empty():
            yield self.queue.get()

    def init(self):
        """Метод инициализации нового процесса"""

    def processing(self):
        raise NotImplementedError(f'{self.__class__.__name__}.processing not implemented')

    def on_process(self):
        self.init()

        while self.on_while.value:
            self.processing()

        while not self.queue.empty():
            self.processing()

        assert self.queue.empty() and self.queue.qsize() == 0, 'Очередь должка быть пустой'


class SubProcessController(object):
    """Контроллер"""

    queue: Queue
    on_while: ValueProxy[bool]

    worker_class: type[SubProcessWorker] = SubProcessWorker
    worker: SubProcessWorker

    worker_process: Process

    def make_worker(self) -> worker_class:
        return self.worker_class(self.on_while, self.queue)

    def start(self):
        """Запуск процесса контроллера"""

        self.on_while = start_tracking()
        self.queue = Queue()

        self.worker = self.make_worker()

        self.worker_process = Process(target=self.worker.on_process)
        self.worker_process.start()

    def stop(self):
        """Передача сигнала для остановки процесса процесса контроллера"""

        self.on_while.value = False

        while self.worker_process.is_alive():
            sleep(1)

    def restart(self):
        if self.on_while is not None and self.on_while.value:
            self.stop()

        self.start()
