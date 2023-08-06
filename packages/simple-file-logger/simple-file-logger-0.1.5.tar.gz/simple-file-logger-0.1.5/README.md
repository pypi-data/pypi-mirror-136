# Simple File Logger

This python package provides a `Logger` class which is easy to use
for basic logging to files.

## Install

```sh
pip install simple-file-logger
```

## Usage

```py
from simple_file_logger import Logger

logger = Logger("my_log_file", "path/to/log/directory")
logger.info("Hello!")

# writes to `my_log_file_YYYYMMDD_HHMM_SS.log`
# 2022-01-26 11:57:14,182 - INFO - Hello!
```

The constructor provides various options to configure the logger.

```py
logfile_name: str,
log_dir: Union[Path, str, None]=None,
level=logging.DEBUG,
mode="w",
add_timestamp_to_filename=True,
is_console_only=False,
is_null_handler=False,
is_rolling_handler=False,
process: str = None,
```

- To create a console-only handler, pass an empty string for the first argument, and set `is_console_only` to `True`.
- The `is_rolling_handler` parameter controls whether the logger automatically writes to a new file when the existing one becomes larger than `5mb`. It will archive the current log with a serial number and transition to a new file automatically. The limit of archived files is `5` so the oldest one will get deleted when archiving for the 6th time.
- The `is_null_handler` parameter initializes a logger that does nothing. This is useful for unit testing libraries where functions log messages but you don't want any actual logging to take place.
- The `process` parameter is a little addition to provide some info about what process the currently running script represents. It can be any arbitrary string, such as `downloading_data` or `monitoring_files` etc. This process will also appear on each log line. As the script executes, you can set the `process` in the logger object to a new value. This is helpful for producing files which facilitate easy line extraction related to a specific process when the file is big.

  ```py
  logger.process = "downloading_file"
  # ... logic to download some file which does some logging.
  # The lines will have `downloading_file` before the log message.

  # update file contents
  logger.process = "update_contents"  # set process to indicate the context of log messages to follow

  # ... logic to update file contents and do some logging.

  # no need for further process logs, and just want to log messages.
  logger.process = ""  # prevents addition of process string to log message.

  ```
