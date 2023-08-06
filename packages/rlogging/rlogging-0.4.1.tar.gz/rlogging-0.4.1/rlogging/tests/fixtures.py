from multiprocessing import Manager

import pytest
from rlogging import get_logger
from rlogging.controllers import logging_controller, set_handlers
from rlogging.tests.handlers import PytestLoggingHandler

record_args = ('arg_1', 'arg_2')
record_kwargs = {'kwarg_1': 1, 'kwarg_2': 2}


@pytest.fixture()
def rlogging_records():
    return Manager().list()


@pytest.fixture()
def rlogging_setup_handler_class():
    return PytestLoggingHandler


@pytest.fixture()
def rlogging_setup(rlogging_setup_handler_class, rlogging_records):  # noqa: WPS442
    set_handlers(rlogging_setup_handler_class(rlogging_records))


@pytest.fixture()
def rlogging(rlogging_setup):  # noqa: WPS442

    yield

    logging_controller.stop()


@pytest.fixture()
def rlogger(rlogging):  # noqa: WPS442
    return get_logger('testing')


@pytest.fixture()
def rlogging_log(rlogger):  # noqa: WPS442
    return rlogger.log(5, 'message', *record_args, **record_kwargs)
