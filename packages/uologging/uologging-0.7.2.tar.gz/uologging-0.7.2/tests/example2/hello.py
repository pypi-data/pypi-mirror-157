# hello.py
import logging
import uologging

logger = logging.getLogger(__name__)
trace = uologging.trace(logger)


@trace
def hello():
    print('hello from example2!')
