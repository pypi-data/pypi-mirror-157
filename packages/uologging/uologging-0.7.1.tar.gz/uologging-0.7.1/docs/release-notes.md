We follow [semantic versioning convention](https://semver.org/) for this tool.

## 0.7.1

* Enable using uologging `init...` methods with multiple packages.
* Now using [Hatch](https://github.com/pypa/hatch) for managing development environments, CICD, and builds.
* The following aliases have been added:
```
init_console = init_console_logging
init_syslog = init_syslog_logging
set_verbosity = set_logging_verbosity
```

## 0.7.0

* Added `name` parameter to all logger-configuring functions. Allowing configuring particular loggers (instead of always configuring the root logger).

## 0.6.1

* Fix the `trace` function context, to show the correct file and line number of the invoked function.
    *  Only works for Python >= 3.8

## 0.6.0

* The `trace` function decorator now takes an optional "capture_args" argument.

## 0.5.0

* NOT Backwards Compatible: No longer require the 'root package name' argument.
    * We are now using the true "root" logger provided by logging (instead of working on the parent package)
* Provide a `trace` function decorator that will log at start and end of a function, and the elapsed time of the function.
* 'Initialize' functions can be called multiple times, but will only run one-time.
    * This enables the 'init__logging' functions to be called during module initialization without fear of duplicate logging handlers accidentally getting initialized.

## 0.4.0

* NOT Backwards Compatible: The verbosity_flag is now required for 'set_logging_verbosity' function.

## 0.3.0

* NOT Backwards Compatible: Remove optional verbosity flag from 'init_console_logging' function.
* Enable syslog logging.

## 0.2.1

* Documentation updates.

## 0.2.0

* Provide `add_verbosity_flag` function, as an alternate method to enable '-vv' in CLI tools.

## 0.1.0

* Enable pretty console logging for an entire package.
* Provide argparse 'parent parser' solution, enabling '-vv' in CLI tools.