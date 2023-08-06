# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .EnvironmentVariableConfigurationProvider import (
    EnvironmentVariableConfigurationProvider,
)
from .GremlinConfiguration import GremlinConfiguration
from .GremlinConfigurationResolver import GremlinConfigurationResolver

logger = logging.getLogger(f"{logger_name}.{__name__}")


class EnvironmentVariableConfigurationResolver(GremlinConfigurationResolver):
    """
    Configuration Resolver for the :ref:`EnvironmentVariableConfigurationProvider`

    This is the default :ref:`GremlinConfigurationResolver` used
    """

    @classmethod
    def get_config(self) -> GremlinConfiguration:
        return EnvironmentVariableConfigurationProvider()
