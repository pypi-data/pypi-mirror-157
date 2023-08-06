# hello.py
import logging

import uologging

logger = logging.getLogger(__name__)


@uologging.trace(logger)
def hello():
    print('hello from example!')
