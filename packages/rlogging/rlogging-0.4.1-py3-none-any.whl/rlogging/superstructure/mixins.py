from rlogging.records import Record
from rlogging.superstructure.formatters import BaseFormatter


class FilterLoggerHandlerMixin(object):
    """Миксин, фильтрующий логи по логерам, которые их сделали"""

    loggers: list[str] | None
    exclude_loggers: list[str] | None

    def __init__(self, *args, loggers: list[str] | None = None, exclude_loggers: list[str] | None = None, **kwargs) -> None:
        self.loggers = loggers
        self.exclude_loggers = exclude_loggers

        return super().__init__(*args, **kwargs)

    def settings_check(self):
        is_loggers = self.loggers is not None
        is_exclude_loggers = self.exclude_loggers is not None

        assert is_loggers or is_exclude_loggers, 'Нужно передать хотя бы один из параметров: "loggers" / "exclude_loggers"'

        assert not (is_loggers and is_exclude_loggers), 'Параметры "loggers" и "exclude_loggers" нельзя совмещать'

        return super().settings_check()

    def processing(self, record: Record):
        if (self.loggers is not None and record.logger_name in self.loggers) or (
            self.exclude_loggers is not None and record.logger_name not in self.exclude_loggers
        ):
            return super().processing(record)


class FilterLogLevelHandlerMixin(object):
    """Миксин, фильтрующий логи по уровню лога"""

    level: int

    def __init__(self, *args, level: int, **kwargs) -> None:
        self.level = level

        return super().__init__(*args, **kwargs)

    def processing(self, record: Record):
        if record.level >= self.level:
            return super().processing(record)


class FormatterHandlerMixin(object):
    """Миксин, для использования сущности форматеров"""

    def __init__(self, formatter: BaseFormatter) -> None:
        self.formatter = formatter

        super().__init__()

    def settings_check(self):
        assert isinstance(self.formatter, BaseFormatter), 'Не установлен форматер'

        return super().settings_check()
