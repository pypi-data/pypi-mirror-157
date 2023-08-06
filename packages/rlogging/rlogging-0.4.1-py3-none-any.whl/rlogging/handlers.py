from rlogging.records import Record


class Handler(object):
    """Базоый класс хендлера"""

    def __init__(self) -> None:
        self.settings_check()

    def init(self):
        """Метод инициализации хендлера внутри дочернего процесса"""

    def processing(self, record: Record):
        """Обработка лога хендлером

        Args:
            record (Record): Обрабатываемый лог

        Raises:
            NotImplementedError: _description_
        """

        raise NotImplementedError('Не переопределен метод "processing" базового Хендлера')

    def settings_check(self):
        """Проверка, что хедер настроен правильно"""
