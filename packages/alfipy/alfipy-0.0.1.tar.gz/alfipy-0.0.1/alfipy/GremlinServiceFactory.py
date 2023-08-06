# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import AlfiConstants, logger_name
from .ApplicationCoordinates import ApplicationCoordinates
from .ApiGremlinService import ApiGremlinService
from .GremlinApiClientFactory import GremlinApiClientFactory
from .GremlinConfigurationResolver import GremlinConfigurationResolver
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .GremlinService import GremlinService
from .PassthroughGremlinService import PassthroughGremlinService
from .SystemGremlinConfigurationResolver import (
    SystemGremlinConfigurationResolver,
)

from typing import Optional

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinServiceFactory:
    """
    A user  obtains an instance of :class:`GremlinService` by invoking
    :class:`GremlinServiceFactory()`.:meth:`get_gremlin_service()`

    The :class:GremlinServiceFactory accepts :class:`GremlinCoordinatesProvider`
    and optionally :class:`GremlinConfigurationResolver`

    This object is intended to a singleton, as is the returned :class:`GremlinService`
    """

    _instance = None

    def __init__(
        self,
        coordinates_provider: GremlinCoordinatesProvider,
        configuration_resolver: Optional[GremlinConfigurationResolver] = None,
    ) -> None:
        self._coordinates_provider = coordinates_provider
        if configuration_resolver:
            self._configuration_resolver = configuration_resolver
        else:
            self._configuration_resolver = SystemGremlinConfigurationResolver()

    def __new__(cls, coordinates_provider, configuration_resolver):
        if cls._instance is None:
            cls._instance = super(GremlinServiceFactory, cls).__new__(cls)
        return cls._instance

    def get_gremlin_service(
        self,
        application_coordinates: Optional[ApplicationCoordinates] = None,
        api_client_factory: Optional[GremlinApiClientFactory] = None,
    ) -> GremlinService:
        try:
            if not api_client_factory:
                api_client_factory = GremlinApiClientFactory()
            if not application_coordinates:
                application_coordinates = (
                    self._coordinates_provider.initialize_coordinates()
                )
            if application_coordinates is None:
                team_id = (
                    self._configuration_resolver.get_resolved_config().gremlin_team_id
                )
                logger.error(
                    f"Gremlin could not detect application type. Not enabled for Team {team_id}"
                )
                return PassthroughGremlinService()
            customer_configuration = (
                self._configuration_resolver.get_resolved_config()
            )
            if customer_configuration:
                logger.info(
                    f"Gremlin enabled for Team {customer_configuration.gremlin_team_id}"
                )
                logger.info(
                    f"Application Coordinates found {application_coordinates}"
                )
                api_client = api_client_factory.get_api_client(
                    customer_configuration
                )
                return ApiGremlinService(
                    application_coordinates,
                    self._coordinates_provider,
                    api_client,
                )
        except Exception as e:
            logger.error(
                f"Gremlin Encountered error during configuration - not enabled: {e}"
            )
            return PassthroughGremlinService()
