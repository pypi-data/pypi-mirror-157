# std
import logging
import os
import sys
import traceback
from typing import Optional as Opt, Union

# constants
FMT = '%(asctime)s [%(levelname)s] %(message)s'
ENVIRONMENT_LOG_LEVEL = os.environ.get('LOG_LEVEL', '').upper()

# loggers
_loggers = {}


def get_logger(
        name: str = 'laz',
        level: Opt[Union[int, str]] = None,
        verbosity: Opt[int] = None,
        default_level: Opt[Union[int, str]] = None,
) -> logging.Logger:
    if name in _loggers:
        logger = _loggers[name]
    else:
        logger = _get_logger(name, default_level)
        _loggers[name] = logger

    if level is not None:
        if isinstance(level, str):
            logger.setLevel(level.upper())
        else:
            logger.setLevel(level)

    if verbosity is not None and verbosity > 0:
        logger.setLevel(_convert_verbosity_to_level(verbosity))

    return logger


def _get_logger(
        name: str,
        default_level: Opt[Union[int, str]] = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt=FMT))
    logger.addHandler(handler)

    if default_level is not None and isinstance(default_level, str):
        default_level = default_level.upper()

    try:
        logger.setLevel(ENVIRONMENT_LOG_LEVEL or default_level or 'WARNING')
    except ValueError as e:
        logger.warning(f'Unknown log level: {ENVIRONMENT_LOG_LEVEL}\n{e}\n{traceback.format_exc()}')
    return logger


def _convert_verbosity_to_level(verbosity: int) -> int:
    if verbosity <= 0:
        return logging.WARNING
    elif verbosity == 1:
        return logging.INFO
    elif verbosity >= 2:
        return logging.DEBUG
    elif verbosity >= 3:
        return 5
    elif verbosity >= 4:
        return 1
    else:
        return logging.WARNING

