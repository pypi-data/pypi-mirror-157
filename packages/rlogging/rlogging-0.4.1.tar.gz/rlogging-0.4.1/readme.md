# rlogging

Модуль гибкого логирования приложений python

## Quick start

```bash
pip install rlogging
```

### Настройка

```python
from rlogging import set_handlers, Handler, Record
from rlogging.superstructure.handlers import ConsoleHandler


class YourCustomHandler(Handler):
    """Ваш особенный обработчик, который будет обрабатывать логи"""

    def processing(self, record: Record):
        record.__dd__

# Добавляем в список обработчиков ваш особый обработчик и обработчик для вывода сообщении в консоль:
set_handlers(ConsoleHandler(), YourCustomHandler())
```

### Использование

```python
from rlogging import logger, get_logger

record = logger.log(10, 'log on main logger')
assert record.logger_name == 'main'

logger = get_logger(__name__)
record = logger.log(10, 'log on main logger')
assert record.logger_name == __name__

logger.debug('debug log')
logger.info('info log')
logger.warning('warning log')
logger.error('error log')
logger.critical('critical log')

exception = RuntimeError('some error')
record = logger.exception(exception)
assert record.message == 'RuntimeError: some error'
```

## Django Integration

rlogging может работать с django. Rlogging настроится и запустится вместе с django и сможет использовать django модели.

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_rlogging',
    ...
]
```

### Model Handler

Пример интеграции с django - обработчик, сохраняющий записи в БД.

```python
from rlogging import logger
from django_rlogging.models import RLoggingLog
from django_rlogging.handlers import ModelHandler

set_handlers(ModelHandler())

record = rlogger.debug('test')
model_record = RLoggingLog.objects.first()

assert record.message == model_record.message
assert record.pid_id == model_record.pid_id
```
