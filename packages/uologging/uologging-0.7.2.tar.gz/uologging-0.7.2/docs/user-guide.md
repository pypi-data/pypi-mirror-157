UOLogging is a solution for configuring Python's built-in logging module.

> As of 0.7.1, there are public aliases of all this package unctions to remove the redundant word, "logging".
> I.e., the following aliases have been added.
> 
> ```
> init_console = init_console_logging
> init_syslog = init_syslog_logging
> set_verbosity = set_logging_verbosity
> ```
> 
> TODO: Update these docs to use these shorter aliases, deprecate the long names somehow...

## Enable console logging

Simply call "`init_console_logging()`" to initializing Python's root logger to log to console:

    # ⚠ Inadvisable: Enable logging for ALL python packages/modules
    uologging.init_console_logging()

> ⚠ WARNING: It is inadvisable to "init" the overall root logger except for debugging. 
> Why? The console can get *very noisy* when using 3rd party libraries (that use Python `logging` module).

In general, you will want to specify your package name. To enable logging within your package only, you can provide your package name.

> The handy invocation of `__name__.split('.')[0]` will provide your package's name from *anywhere within your package*.

    # ✅ Best Practice: Enable logging only for your package.
    my_package_name = __name__.split('.')[0]
    uologging.init_console_logging(my_package_name)



## Enable (Linux) syslog logging

Similarly, you can call "`init_syslog_logging()`":

    # Best Practice: Enable logging for your python package
    my_package_name = __name__.split('.')[0]
    uologging.init_syslog_logging(my_package_name)

    # Inadvisable: Enable logging for ALL python packages/modules
    uologging.init_syslog_logging()

## Set Logging Verbosity

> Per Python logging suggestion: WARNING, ERROR, and CRITICAL messages are all logged by default.

If you are interested in seeing the DEBUG and INFO log messages, you'll need to update the logging verbosity in your application.
We provide the method set_logging_verbosity() for this purpose.
Higher number means more logging. 

> Choices are [0,2].
> Default is 0. Default will captures WARNING, ERROR, and CRITICAL logs.
> Provide 1 to also capture INFO logs. 
> Provide 2 to also capture DEBUG logs.

    # Enable maximum logging for your python package
    my_package_name = __name__.split('.')[0]
    uologging.set_logging_verbosity(2, args.verbosity_flag, my_package_name)

    # Enable maximum logging for ALL python packages/modules
    uologging.set_logging_verbosity(2)

## argparse 'verbosity flag'

For CLI tools, we provide an integration with argparse to set the logging verbosity.
This integration enables the tool's user to add `-vv` at the command-line for maximum logging verbosity.

> `-v` will enable INFO messages, but not DEBUG.

The verbosity_flag can be gathered via argparse using "`add_verbosity_flag(parser)`":

    import uologging
    import argparse

    parser = argparse.ArgumentParser()
    uologging.add_verbosity_flag(parser)

    args = parser.parse_args(['-vv'])
    # args.verbosity_flag == 2

Now, simply call "`set_logging_verbosity()`" with `args.verbosity_flag` for your package:

    my_package_name = __name__.split('.')[0]
    uologging.set_logging_verbosity(args.verbosity_flag, my_package_name)

> Alternately, if you are comfortable with argparse 'Parent parsers', you can integrate with argparse using use get_default_parser() as a parent parser.

    # Alternate 'Parent parser' argparse integration
    parser = argparse.ArgumentParser(parents=[
        uologging.get_default_parser(),
    ])

### Example: Configuring CLI tool with console & syslog logging

Let's imagine you have a package "`examplepkg`" with a CLI tool in the "`mytool`" module.

    # my_cli_tool.py
    import argparse
    import uologging

    # Parse CLI arguments, '-vv' will result in maximum logging verbosity.
    parser = argparse.ArgumentParser()
    uologging.add_verbosity_flag(parser)
    args = parser.parse_args()

    # Initialize logging
    my_package_name = __name__.split('.')[0]
    uologging.init_console_logging(my_package_name)
    uologging.init_syslog_logging(my_package_name)
    uologging.set_logging_verbosity(args.verbosity_flag, my_package_name)

### Logging messages format

The formatting for log messages is specified in the (private) `uologging._logging_format` variable.

Here are a couple of lines showing what you can expect your logs to looks like:

    2022-01-07 15:40:09 DEBUG    Some simle message for you [hello.py:10]
    2022-01-07 15:40:09 DEBUG    Finished: example.hello:hello((),{}) [hello.py:10] 
    2022-01-07 15:40:09 DEBUG    example.hello:hello((),{}) execution time: 0.00 sec [hello.py:10] 


## Tracing a function

There is a simple `trace` decorator you can use in your python modules to log the 'execution time' of any of your functions.

> The trace decorator logs at DEBUG severity.
> So, call `set_logging_verbosity(>=2)` to see the trace messages in your logs.

    # hello.py
    import logging
    import uologging

    logger = logging.getLogger(__name__)

    @uologging.trace(logger)
    def hello():
        print('hello!')
    
    hello()

Expect the following messages to be logged:

    2022-01-07 15:40:09 DEBUG    Starting: example.hello:hello((),{}) [hello.py:10]
    hello!
    2022-01-07 15:40:09 DEBUG    Finished: example.hello:hello((),{}) [hello.py:10] 
    2022-01-07 15:40:09 DEBUG    example.hello:hello((),{}) execution time: 0.00 sec [hello.py:10] 

## `logging` Best Practices

Use the Python logging package per the following best practices:

1. `logger = logging.getLogger(__name__)` to get the logger for each module/script.
2. Then, use `logger.debug()`, `logger.info()`, `logger.warning()`, etc to add tracing to your Python modules/scripts.

### Example

A trivial example demonstrating best practices:

    # hello.py
    import logging

    logger = logging.getLogger(__name__)

    def hello():
        logger.debug('About to say "hello!"')
        print('hello!')
        logger.debug('Said "hello!"')
