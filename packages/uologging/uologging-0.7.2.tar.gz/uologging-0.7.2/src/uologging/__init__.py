from distutils.log import set_verbosity

from uologging.cli import add_verbosity_flag, get_default_parser
from uologging.performance import trace
from uologging.uologging import (init_console_logging, init_syslog_logging,
                                 set_logging_verbosity)

init_console = init_console_logging
init_syslog = init_syslog_logging
set_verbosity = set_logging_verbosity

__version__ = '0.7.2'
__all__ = [
    'trace',
    'init_console_logging', 
    'init_console', 
    'init_syslog_logging',
    'init_syslog',
    'set_logging_verbosity', 
    'set_verbosity',
    'get_default_parser', 
    'add_verbosity_flag', 
]
