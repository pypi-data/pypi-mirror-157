import uologging

import example.hello

uologging.init_console_logging()
uologging.set_logging_verbosity(2)

# Invoke a function that has uologging tracing enabled
example.hello.hello()
