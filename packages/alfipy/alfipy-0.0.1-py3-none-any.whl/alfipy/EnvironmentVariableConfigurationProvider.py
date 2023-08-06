# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import os

from .AlfiConstants import logger_name
from .EnvironmentVariableNameKeys import EnvironmentVariableNameKeys as ENVARS
from .GremlinConfiguration import GremlinConfiguration

from dataclasses import dataclass, field


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class EnvironmentVariableConfigurationProvider(GremlinConfiguration):
    """
    Built-in :ref:`GremlinConfiguration` implementation to convert environment variables
    into a configuration object
    """

    def __post_init__(self) -> None:
        logger.info(
            "Gremlin ALFI obtaining configuration from environment variables"
        )
        self.gremlin_identifier = os.getenv(ENVARS.gremlin_identifier, None)
        self.gremlin_team_id = os.getenv(ENVARS.gremlin_team_id, None)
        self.cache_interval_in_ms = os.getenv(
            ENVARS.cache_interval_in_ms, 2000
        )
        self.http_proxy = os.getenv(ENVARS.http_proxy, None)
        self.certificate_or_file_reference = os.getenv(
            ENVARS.certificate_or_file_reference, None
        )
        self.private_key_or_file_reference = os.getenv(
            ENVARS.private_key_or_file_reference, None
        )
