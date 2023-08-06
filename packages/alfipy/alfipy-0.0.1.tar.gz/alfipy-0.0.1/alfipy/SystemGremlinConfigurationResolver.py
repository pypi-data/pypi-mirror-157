# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .GremlinConfiguration import GremlinConfiguration
from .GremlinConfigurationResolver import GremlinConfigurationResolver

from typing import ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


class SystemGremlinConfigurationResolver(GremlinConfigurationResolver):
    """
    This is the default implementation of :class:GremlinConfigurationResolver
    It provides an instance of :class:GremlinConfiguration by looking in
    `gremlin.properties` and environment-variables
    """

    GREMLIN_ENABLED_ENV_VAR_NAME: ClassVar[str] = "GREMLIN_ALFI_ENABLED"
    GREMLIN_IDENTIFIER_ENV_VAR_NAME: ClassVar[str] = "GREMLIN_ALFI_IDENTIFIER"
    GREMLIN_TEAM_ID_ENV_VAR_NAME: ClassVar[str] = "GREMLIN_TEAM_ID"
    GREMLIN_TEAM_PRIVATE_KEY_ENV_VAR_NAME: ClassVar[
        str
    ] = "GREMLIN_TEAM_PRIVATE_KEY_OR_FILE"
    GREMLIN_TEAM_CERTIFICATE_ENV_VAR_NAME: ClassVar[
        str
    ] = "GREMLIN_TEAM_CERTIFICATE_OR_FILE"
    GREMLIN_CACHE_REFRESH_INTERVAL_ENV_VAR_NAME: ClassVar[
        str
    ] = "GREMLIN_REFRESH_INTERVAL_MS"
    HTTP_PROXY: ClassVar[str] = "http_proxy"

    PROPERTIES_FILE_NAME: ClassVar[str] = "gremlin.properties"

    @classmethod
    def get_config(cls) -> GremlinConfiguration:
        pass
