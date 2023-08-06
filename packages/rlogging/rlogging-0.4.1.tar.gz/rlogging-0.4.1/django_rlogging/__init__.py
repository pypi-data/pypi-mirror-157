"""Интеграция rlogging с django

Настройки settings.py

RLOGGING_NOT_USE - Не запускать модуль django_rlogging.
    При половительном значении переменной все логи, которые будут генерироваться с помощью логгеров rlogging, будут удаляться.

RLOGGING_SETUP - Каллбек функция пользовательской настройки логеров, которая будет вызвана при инициализации компонента.

"""

try:
    import django

except ImportError:
    raise ImportError('Модуль django_rlogging требует с установленным django')

import rlogging

__version__ = rlogging.__version__

if django.VERSION < (3, 2):
    default_app_config = 'django_rlogging.RLoggingAppConfig'
