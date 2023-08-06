# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_rlogging',
 'django_rlogging.migrations',
 'rlogging',
 'rlogging.superstructure',
 'rlogging.tests']

package_data = \
{'': ['*']}

install_requires = \
['execution-controller']

setup_kwargs = {
    'name': 'rlogging',
    'version': '0.4.1',
    'description': 'Модуль гибкого логирования python приложений',
    'long_description': '# rlogging\n\nМодуль гибкого логирования приложений python\n\n## Quick start\n\n```bash\npip install rlogging\n```\n\n### Настройка\n\n```python\nfrom rlogging import set_handlers, Handler, Record\nfrom rlogging.superstructure.handlers import ConsoleHandler\n\n\nclass YourCustomHandler(Handler):\n    """Ваш особенный обработчик, который будет обрабатывать логи"""\n\n    def processing(self, record: Record):\n        record.__dd__\n\n# Добавляем в список обработчиков ваш особый обработчик и обработчик для вывода сообщении в консоль:\nset_handlers(ConsoleHandler(), YourCustomHandler())\n```\n\n### Использование\n\n```python\nfrom rlogging import logger, get_logger\n\nrecord = logger.log(10, \'log on main logger\')\nassert record.logger_name == \'main\'\n\nlogger = get_logger(__name__)\nrecord = logger.log(10, \'log on main logger\')\nassert record.logger_name == __name__\n\nlogger.debug(\'debug log\')\nlogger.info(\'info log\')\nlogger.warning(\'warning log\')\nlogger.error(\'error log\')\nlogger.critical(\'critical log\')\n\nexception = RuntimeError(\'some error\')\nrecord = logger.exception(exception)\nassert record.message == \'RuntimeError: some error\'\n```\n\n## Django Integration\n\nrlogging может работать с django. Rlogging настроится и запустится вместе с django и сможет использовать django модели.\n\n```python\n# settings.py\nINSTALLED_APPS = [\n    ...\n    \'django_rlogging\',\n    ...\n]\n```\n\n### Model Handler\n\nПример интеграции с django - обработчик, сохраняющий записи в БД.\n\n```python\nfrom rlogging import logger\nfrom django_rlogging.models import RLoggingLog\nfrom django_rlogging.handlers import ModelHandler\n\nset_handlers(ModelHandler())\n\nrecord = rlogger.debug(\'test\')\nmodel_record = RLoggingLog.objects.first()\n\nassert record.message == model_record.message\nassert record.pid_id == model_record.pid_id\n```\n',
    'author': 'rocshers',
    'author_email': 'prog.rocshers@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
