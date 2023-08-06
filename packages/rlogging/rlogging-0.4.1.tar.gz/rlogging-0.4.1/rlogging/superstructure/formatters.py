import json

from rlogging.records import Record


class BaseFormatter(object):
    """Базоый форматер логов.

    Форматер - инструмент для преобразования лога в строку в настраиваемом формате


    """

    def __init__(self) -> None:
        self.settings_check()

    def settings_check(self):
        """Проверка, что форматер настроен правильно"""

    def formatting(self, record: Record) -> str:
        raise NotImplementedError('Не переопределен метод "formatting" базового Форматера')

    def __call__(self, record: Record) -> str:
        return self.formatting(record)


class TemplateFormatter(BaseFormatter):
    """Форматер, преобразующий запись лога в строку по шаблону"""

    default_template = '{level_label_center}:{logger_name}:{message}'

    template: str

    def __init__(self, template: str) -> None:
        self.template = template

        super().__init__()

    def formatting(self, record: Record) -> str:
        return self.template.format(**record.__dict__)


class StructureFormatter(BaseFormatter):
    """Форматер, преобразующий запись лога в json объект с определенным множеством полей"""

    fields: list[str] | None
    exclude_loggers: list[str] | None

    def __init__(self, fields: list[str] = None, exclude_loggers: list[str] = None) -> None:
        self.fields = fields
        self.exclude_loggers = exclude_loggers

        super().__init__()

    def settings_check(self):
        """Проверка, что форматер настроен правильно"""

        assert self.fields is None or self.exclude_loggers is None, 'Параметры "target_loggers" и "exclude_loggers" нельзя совмещать'

        if self.fields is not None:  # noqa: SIM102
            if miss_fields := set(self.fields) - set(Record.__all_slots__):
                raise AssertionError(f'Поля "{miss_fields}" не является атрибутом объекта лога')

        if self.exclude_loggers is not None:  # noqa: SIM102
            if miss_fields := set(self.exclude_loggers) - set(Record.__all_slots__):
                raise AssertionError(f'Поля "{miss_fields}" не является атрибутом объекта лога')

        return super().settings_check()

    def formatting(self, record: Record) -> str:
        if self.fields is not None:
            return json.dumps(
                {
                    record_field_name: record_field_value
                    for record_field_name, record_field_value in record.__dict__.items()
                    if record_field_name in self.fields
                }
            )

        if self.exclude_loggers is not None:
            return json.dumps(
                {
                    record_field_name: record_field_value
                    for record_field_name, record_field_value in record.__dict__.items()
                    if record_field_name not in self.exclude_loggers
                }
            )

        return json.dumps(record.__dict__)
