# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .AlfiConstants import logger_name

from dataclasses import dataclass, field
from typing import ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class AlfiConfig(metaclass=ABCMeta):
    """
    ALFI Configuration Interface

    """

    default_cache_refresh_interval_in_ms: ClassVar[int] = 10_000
    minimum_valid_cache_refresh_interval_in_ms: ClassVar[int] = 1_000
    maximum_valid_cache_refresh_interval_in_ms: ClassVar[int] = 5 * 60 * 1000

    cache_interval_in_ms: int
    _cache_interval_in_ms: int = field(
        default=default_cache_refresh_interval_in_ms, init=False, repr=False
    )

    client_identifier: str = field(default="")
    gremlin_team_id: str = field(default="")

    @property
    @abstractmethod
    def auth_header_value(self):
        raise NotImplementedError("Method needs to implemented in subclass")

    @property
    @abstractmethod
    def certificate(self) -> str:
        raise NotImplementedError("Method needs to implemented in subclass")

    @property
    @abstractmethod
    def private_key(self) -> str:
        raise NotImplementedError("Method needs to implemented in subclass")

    @property
    def cache_interval_in_ms(self) -> int:
        return self._cache_interval_in_ms

    @cache_interval_in_ms.setter
    def cache_interval_in_ms(self, value: int) -> None:
        if value and type(value) == int:
            self._cache_interval_in_ms = self.constrain_cache_refresh_interval(
                value
            )

    @classmethod
    def constrain_cache_refresh_interval(cls, input: int) -> int:
        if not input:
            logger.info(
                "Gremlin ALFI experiment cache refresh interval (ms) configuration was not provided. "
                + f"Using default value of {cls.default_cache_refresh_interval_in_ms}"
            )
            return cls.default_cache_refresh_interval_in_ms
        if input < 0:
            logger.error(
                "Gremlin ALFI experiment cache refresh interval (ms) must be positive! "
                + f"Using default value of {cls.default_cache_refresh_interval_in_ms}"
            )
            return cls.default_cache_refresh_interval_in_ms
        if input < cls.minimum_valid_cache_refresh_interval_in_ms:
            logger.error(
                "Gremlin ALFI experiment cache refresh interval (ms) must be at least "
                + f"{cls.minimum_valid_cache_refresh_interval_in_ms}! "
                + f"Using value of {cls.minimum_valid_cache_refresh_interval_in_ms}"
            )
            return cls.minimum_valid_cache_refresh_interval_in_ms
        if input > cls.maximum_valid_cache_refresh_interval_in_ms:
            logger.error(
                "Gremlin ALFI experiment cache refresh interval (ms) must be at most "
                + f"{cls.maximum_valid_cache_refresh_interval_in_ms}! "
                + f"Using value of {cls.maximum_valid_cache_refresh_interval_in_ms}"
            )
            return cls.maximum_valid_cache_refresh_interval_in_ms
        return input
