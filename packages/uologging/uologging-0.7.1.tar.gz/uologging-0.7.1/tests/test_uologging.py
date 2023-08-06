import uologging
from assertpy import assert_that

import example2.hello
import example.hello


def test_init_console_logging(caplog):
    # Arrange
    uologging.init_console_logging('example')
    uologging.set_logging_verbosity(2, 'example')

    # Act -- do things that cause logging to occur
    example.hello.hello()

    # Assert
    assert_that(caplog.text).contains('Starting: example.hello:hello')


def test_init_console_logging_2_packages(caplog):
    # Arrange
    uologging.init_console_logging('example')
    uologging.set_logging_verbosity(2, 'example')
    uologging.init_console_logging('example2')
    uologging.set_logging_verbosity(2, 'example2')

    # Act -- do things that cause logging to occur
    example.hello.hello()
    example2.hello.hello()

    # Assert
    assert_that(caplog.text).contains('Starting: example.hello:hello')
    assert_that(caplog.text).contains('Starting: example2.hello:hello')
