# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name

from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import wraps
from time import monotonic, sleep, time_ns
from typing import Callable

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinTime(metaclass=ABCMeta):
    """
    Abstraction of all time-related events for ALFI
    """

    _instance = None

    def __init__(self):
        pass

    @abstractmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GremlinTime, cls).__new__(cls)
        return cls._instance

    @staticmethod
    @abstractmethod
    def advance_millis(millis_to_advance: int) -> None:
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @staticmethod
    @abstractmethod
    def get_current_time_in_ms() -> float:
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @classmethod
    def system(cls) -> GremlinTime:
        return SystemTime()

    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        """
        Measure and log the execution time of a method

        :param func:
        :return:
        """

        @wraps(func)
        def measure_time(*args, **kwargs):
            start = monotonic()
            inner_call = func(*args, **kwargs)
            time_delta = monotonic() - start
            if logger.getEffectiveLevel() is logging.DEBUG:
                logger.debug(
                    f"Function: {func.__name__} returned in {time_delta * 1000} ms"
                )
            return inner_call

        return measure_time


class SystemTime(GremlinTime):
    _instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SystemTime, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def advance_millis(millis_to_advance: int) -> None:
        sleep(millis_to_advance / 1000)

    @staticmethod
    def get_current_time_in_ms() -> float:
        dt = datetime.utcnow()
        return dt.timestamp() * 1000

    @staticmethod
    def get_current_time_in_ns() -> float:
        return time_ns()
