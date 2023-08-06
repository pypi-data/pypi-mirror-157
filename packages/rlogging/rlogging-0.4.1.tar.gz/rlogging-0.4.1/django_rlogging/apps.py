from django.apps.config import AppConfig
from django.conf import settings
from django.db import connections

from django_rlogging.utils import get_obj, rlogging_setup_from_data


class RLoggingAppConfig(AppConfig):
    """Конфигурация django приложения для подключения к django"""

    name = 'django_rlogging'
    verbose_name = 'rlogging for django'

    def ready(self):
        connections.close_all()

        if rlogging_data := getattr(settings, 'RLOGGING_SETUP_DATA', None):
            rlogging_setup_from_data(rlogging_data)
            return

        if setup_callback := getattr(settings, 'RLOGGING_SETUP_CALLBACK', None):
            if isinstance(setup_callback, str):
                setup_callback = get_obj(setup_callback)

            if callable(setup_callback):
                setup_callback()
                return

            raise AssertionError('Настройка RLOGGING_SETUP_CALLBACK должна или ссылаться на функцию или является функцией')

        raise AssertionError('Настройка rloggign требует наличие одной из переменных: RLOGGING_SETUP_DATA, RLOGGING_SETUP_CALLBACK')
