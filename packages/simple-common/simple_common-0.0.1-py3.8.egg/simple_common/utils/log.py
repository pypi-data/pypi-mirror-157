import logging
from logging import Logger
from .date import now_str


def basic_log_info(logger: Logger, format_str: str, **kwargs):
    kwargs.update(dict(date=now_str()))
    logger.info(format_str, kwargs)
