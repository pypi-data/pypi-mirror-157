import logging
import sys
import time
from functools import wraps

MAJOR=0
MINOR=1

def pretty_function_with_args_str(func, args, kwargs):
    ret = f'{func.__module__}:{func.__name__}'
    ret += '('
    if args:
        ret += ', '.join(args)
        ret += args
    if kwargs:
        ret += ', '.join([f'{key}={val}' for key, val in kwargs.items()])
    ret += ')'
    return ret


def pretty_function_no_args_str(func):
    return f'{func.__module__}:{func.__name__}(...)'


def trace(logger: logging.Logger, capture_args=True):
    """Decorator to trace the execution time of a Python function or method.

    Uses INFO log level for logging the traced function's "exec time".
    Also will log the traced function's entry and exit at DEBUG log level.

    Args:
        logger (logging.Logger): The logger instance for the function's module.
        capture_args (bool, optional): When tracing the function, capture the 
            arguments provided to the function and add them to the log message.
            Defaults to True.

    Example:

    First, get the logger for your Python module.

        import logging
        logger = logging.getLogger(__name__)

    Then, use the trace_time decorator with that logger as the argument.

        import uologging
        @uologging.trace(logger)
        def my_slow_function():
            import time
            time.sleep(1)
        my_slow_function()
    """
    def _trace_time(func):
        def log_info(msg):
            if sys.version_info[MAJOR] >= 3 and sys.version_info[MINOR] >= 8:
                logger.info(msg, stacklevel=3)
            else:
                logger.info(msg)
        def log_debug(msg):
            if sys.version_info[MAJOR] >= 3 and sys.version_info[MINOR] >= 8:
                logger.info(msg, stacklevel=3)
            else:
                logger.info(msg)
        @wraps(func)
        def timed(*args, **kwargs):
            if capture_args:
                function_str = pretty_function_with_args_str(func, args, kwargs)
            else:
                function_str = pretty_function_no_args_str(func)
            log_debug(f'Starting: {function_str}')
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            log_debug(f'Finished: {function_str}')
            log_info(f'{function_str} exec time: {end - start:.2f} sec')
            return result
        return timed
    return _trace_time
