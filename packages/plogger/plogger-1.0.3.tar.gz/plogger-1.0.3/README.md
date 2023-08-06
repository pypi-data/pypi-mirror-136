[![PyPI version](https://badge.fury.io/py/plogger.svg)](https://badge.fury.io/py/plogger)
[![Build Status](https://travis-ci.org/c-pher/plogger.svg?branch=master)](https://travis-ci.org/c-pher/plogger)
[![Coverage Status](https://coveralls.io/repos/github/c-pher/plogger/badge.svg?branch=master)](https://coveralls.io/github/c-pher/plogger?branch=master)


## Plogger

Plogger - a simple high level logger wrapper to log into console/file with different level. Used built-in logger module.

## Result
```cmd
2020-01-08 02:03:47 [NAME] [LINE:21] [WARNING] log it as warning
2020-01-08 02:03:47 [NAME] [LINE:22] [INFO] log it as info level
```

## Installation
For most users, the recommended method to install is via pip:
```cmd
pip install plogger
```

## Import

```python
from plogger import Logger
```

## Usage

- As standalone logger function:

```python
from plogger import logger


logger = logger('name')
logger.info('test')
```

```commandline
2022-01-10 18:52:32 | INFO | name | test
```

- Or use class Logger

```python
from plogger import Logger

logger = Logger('test', console=True, file=True)  # Log into file too
logger().info('log this')
logger.logger.info('and log this too')
```

- As part of class using inheritance:

```python
from plogger import Logger

class MyClass(Logger):
    def __init__(self, logger_enabled=True, *args, **kwargs):
        super().__init__(name=self.__class__.__name__, enabled=logger_enabled, *args, **kwargs)
    
    def method_name(self):
        self.logger.info('method_name invoked')
```

- Another yet usage way

```python
from plogger import Logger

logger = Logger('NAME').__call__()

logger.warning('log it as warning')
logger.info('log it as info level')
```

## Changelog

##### 1.0.3 (29.01.2022)

Fixed entries duplicating. Added handlers cleaning

##### 1.0.2 (25.01.2022)

console_output=sys.stderr by default

##### 1.0.1 (10.01.2022)

Added console_output=sys.stdout param

##### 1.0.0 (26.01.2020)

Added logger() function