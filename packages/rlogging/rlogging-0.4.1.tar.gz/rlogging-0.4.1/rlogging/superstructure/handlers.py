from rlogging.handlers import Handler
from rlogging.records import Record
from rlogging.superstructure.formatters import BaseFormatter, StructureFormatter, TemplateFormatter
from rlogging.superstructure.mixins import FormatterHandlerMixin


class DevHandler(Handler):
    """Хендлер для разработки.

    Возвращает пришедший лог

    """

    def processing(self, record: Record):
        return record


class ConsoleHandler(FormatterHandlerMixin, Handler):
    """Хендлер, для записи логов в файл"""

    def __init__(self, formatter: BaseFormatter = None) -> None:
        if formatter is None:
            formatter = TemplateFormatter(TemplateFormatter.default_template)

        super().__init__(formatter)

    def processing(self, record: Record):
        print(self.formatter(record))


class FileHandler(FormatterHandlerMixin, Handler):
    """Хендлер, для записи логов в файл"""

    def __init__(self, formatter: BaseFormatter = None) -> None:
        if formatter is None:
            formatter = StructureFormatter()

        super().__init__(formatter)
