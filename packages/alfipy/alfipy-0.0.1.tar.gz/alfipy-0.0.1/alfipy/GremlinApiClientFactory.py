# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import os

from .AlfiConfig import AlfiConfig
from .AlfiConstants import logger_name, service_endpoint, service_version
from .GremlinApiClient import GremlinApiClient
from .GremlinApiClientResolver import GremlinApiClientResolver

from typing import ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinApiClientFactory:
    """
    Instantiate a singleton instance of the :ref:`GremlinAPI` using the :ref:`GremlinApiClientResolver`
    """

    GREMLIN_SERVICE_URL_ENV_VAR_NAME: ClassVar[
        str
    ] = "GREMLIN_ALFI_SERVICE_ENDPOINT"
    GREMLIN_SERVICE_VERSION_ENV_VAR_NAME: ClassVar[
        str
    ] = "GREMLIN_ALFI_SERVICE_VERSION"
    GREMLIN_PROD_ALFI_SERVICE_URL: ClassVar[str] = service_endpoint
    GREMLIN_PROD_ALFI_SERVICE_VERSION: ClassVar[str] = service_version

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GremlinApiClientFactory, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_api_client(cls, alfi_config: AlfiConfig) -> GremlinApiClient:
        service_endpoint_url = os.getenv(
            cls.GREMLIN_SERVICE_URL_ENV_VAR_NAME,
            cls.GREMLIN_PROD_ALFI_SERVICE_URL,
        )
        service_endpoint_version = os.getenv(
            cls.GREMLIN_SERVICE_VERSION_ENV_VAR_NAME,
            cls.GREMLIN_PROD_ALFI_SERVICE_VERSION,
        )
        return GremlinApiClientResolver.get_client(
            alfi_config, service_endpoint_url, service_endpoint_version
        )
