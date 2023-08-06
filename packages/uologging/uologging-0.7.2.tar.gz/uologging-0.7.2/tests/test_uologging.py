import importlib

import pytest
import uologging
from assertpy import assert_that

import example2.hello
import example.hello


@pytest.fixture(autouse=True)
def reload_uologging_module_before_each_test_run():
    # uologging module has some module-variables that we need reset between each test run
    importlib.reload(uologging.uologging)
    yield

def test_init_console_logging(caplog):
    # Arrange
    uologging.init_console_logging('example')
    uologging.set_logging_verbosity(2, 'example')

    # Act -- do things that cause logging to occur
    example.hello.hello()

    # Assert
    assert_that(caplog.text).contains('Starting: example.hello:hello')


def test_init_console_logging_2_packages(capsys):
    # Arrange
    uologging.init_console_logging('example')
    uologging.set_logging_verbosity(2, 'example')
    uologging.init_console_logging('example2')
    uologging.set_logging_verbosity(2, 'example2')

    # Act -- do things that cause logging to occur
    example.hello.hello()
    example2.hello.hello()

    # Assert
    logs = capsys.readouterr().err
    assert_that(logs).contains('Starting: example.hello:hello')
    assert_that(logs).contains('Starting: example2.hello:hello')


def test_init_console_logging_package_twice(capsys):
    # Arrange
    uologging.init_console('example')
    uologging.set_verbosity(2, 'example')
    uologging.init_console('example')
    uologging.set_verbosity(2, 'example')

    # Act -- do things that cause logging to occur
    example.hello.hello()

    # Assert
    logs = capsys.readouterr()
    logs = logs.err
    assert_that(logs).does_not_match(r'(?m)Starting.*\n*.*Starting')
