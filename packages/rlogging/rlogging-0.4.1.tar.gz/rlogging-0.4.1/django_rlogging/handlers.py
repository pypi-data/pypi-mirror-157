from rlogging.handlers import Handler
from rlogging.records import Record

from django_rlogging.models import RLoggingLog


class ModelHandler(Handler):
    """Хендлер сохраняющий логи в БД"""

    def init(self):
        return super().init()

    def processing(self, record: Record):
        RLoggingLog.objects.create(**record.__dict__)
