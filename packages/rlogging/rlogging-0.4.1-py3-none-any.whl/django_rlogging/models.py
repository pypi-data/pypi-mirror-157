from django.db import models
from django.utils.translation import gettext_lazy as gl


class RLoggingLog(models.Model):
    """Модель лога rlogging

    Для сохранения логов в БД нужно подключить хендлер `django_rlogging.handlers.ModelHandler`

    """

    logger_name = models.CharField(gl('Logger name'), max_length=255)  # noqa: WPS432
    level = models.IntegerField(gl('Уровень лога'))
    message = models.CharField(gl('Сообщение'), max_length=255)  # noqa: WPS432
    args = models.JSONField(gl('args'))
    kwargs = models.JSONField(gl('kwargs'))

    timestamp = models.FloatField(gl('kwargs'))
    pid_id = models.IntegerField(gl('Идентификатор процесса'))
    process_name = models.CharField(gl('Имя процесса'), max_length=64)  # noqa: WPS432
    thread_id = models.IntegerField(gl('Идентификатор потока'))

    from_file = models.CharField(gl('Файл, где был сделан лог'), max_length=255)  # noqa: WPS432
    from_file_line = models.CharField(gl('Строка файла ,где был сделан лог'), max_length=255)  # noqa: WPS432
    from_module = models.CharField(gl('Модуль, где был сделан лог'), max_length=255)  # noqa: WPS432
    from_object = models.CharField(gl('Объект, где был сделан лог'), max_length=255)  # noqa: WPS432

    level_label = models.CharField(gl('Преобразованный заголовок уровня лога'), max_length=8)
    level_label_center = models.CharField(gl('Преобразованный и отцентрированный заголовок уровня лога'), max_length=8)

    def __str__(self):
        return self.message
