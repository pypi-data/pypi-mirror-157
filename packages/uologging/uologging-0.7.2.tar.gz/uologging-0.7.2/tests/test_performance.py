
import time
import logging

from assertpy import assert_that

import uologging


def test_trace(caplog):
    # Arrange
    execution_time = 0.1
    with caplog.at_level(logging.DEBUG):
        uologging.init_console_logging()
        logger = logging.getLogger(__name__)

        @uologging.trace(logger)
        def test_method():
            time.sleep(execution_time)

        # Act
        test_method()

    # Assert - May fail on very slow computers...
    assert_that(caplog.text).contains(f'Starting: {__name__}:{test_method.__name__}')
    assert_that(caplog.text).contains(f'Finished: {__name__}:{test_method.__name__}')
    assert_that(caplog.text).contains(f'exec time: {execution_time}')


def test_trace_dont_capture_secret_arguments(caplog):
    # Arrange
    with caplog.at_level(logging.DEBUG):
        uologging.init_console_logging()
        logger = logging.getLogger(__name__)

        @uologging.trace(logger, capture_args=False)
        def test_method(password):
            pass

        # Act
        test_method('SuperSecretPassword')

    # Assert - May fail on very slow computers...
    assert_that(caplog.text).does_not_contain('SuperSecretPassword')
