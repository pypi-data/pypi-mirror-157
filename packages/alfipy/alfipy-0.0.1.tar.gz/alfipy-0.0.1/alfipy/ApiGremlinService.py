# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name, service_url
from .ApplicationCoordinates import ApplicationCoordinates
from .Atomic import AtomicBoolean, AtomicLong, AtomicReference
from .BoundedConcurrentSet import BoundedConcurrentSet
from .ExperimentImpact import ExperimentImpact
from .GremlinApiClient import GremlinApiClient
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .GremlinService import GremlinService
from .GremlinTime import SystemTime
from .Impact import Impact
from .TrafficCoordinates import TrafficCoordinates
from .TrafficQuery import TrafficQuery

from typing import Optional

logger = logging.getLogger(f"{logger_name}.{__name__}")


class ApiGremlinService(GremlinService):
    """
    An instance of :ref:`GremlinService` that makes calls to the Gremlin API. It contains a
    cache of experiments and decouples calls to get an experiment as the customer application
    hits injection points from actual calls to the Gremlin API.

    It does this by maintaining a timestamp of the last call to the API. If an injection point
    occurs and the cache needs a refresh, that call waits for a response from the Gremlin API.
    A successful response overwrites the cache and the time timestamp.
    """

    def __init__(
        self,
        application_coordinates: ApplicationCoordinates,
        gremlin_coordinates_provider: GremlinCoordinatesProvider,
        gremlin_api_client: GremlinApiClient,
        cache_refresh_interval_in_ms: int = 10000,
    ):
        super(ApiGremlinService, self).__init__()
        self._api_client = gremlin_api_client
        self._application_coordinates = application_coordinates
        self._cache_refresh_interval_in_ms = cache_refresh_interval_in_ms
        self._cached_experiments = AtomicReference()
        self._client_registration_complete = AtomicBoolean()
        self._gremlin_coordinates_provider = gremlin_coordinates_provider
        self._impacted_guids = BoundedConcurrentSet()
        self._next_cache_update_timestamp = AtomicLong()

    def __new__(
        cls,
        application_coordinates: ApplicationCoordinates,
        gremlin_coordinates_provider: GremlinCoordinatesProvider,
        gremlin_api_client: GremlinApiClient,
        cache_refresh_interval_in_ms: int = 10000,
    ):
        if cls._instance is None:
            cls._instance = super(ApiGremlinService, cls).__new__(cls)
        return cls._instance

    def get_experiment(
        self, traffic_coordinates: TrafficCoordinates
    ) -> Optional[ExperimentImpact]:
        self.try_update_cache()
        cached_api_response = self._cached_experiments.get()
        if cached_api_response is not None:
            optional_failure = self.determine_if_experiment_applies(
                cached_api_response, traffic_coordinates
            )
            if optional_failure:
                impact_guid = optional_failure.get_experiment_guid()
                if not self._impacted_guids.contains(impact_guid):
                    self._impacted_guids.add(impact_guid)
                    self._api_client.mark_impact(impact_guid)
            return optional_failure
        else:
            return ExperimentImpact("", Impact())

    def has_experiments(self) -> bool:
        self.try_update_cache()
        return bool(self._cached_experiments.get())

    def shutdown(self) -> None:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug("Shutting down Gremlin")
        self._api_client.shutdown()

    def mark_registration_complete(self) -> None:
        self._client_registration_complete.set(True)

    def try_update_cache(self) -> None:
        next_cache_update = self._next_cache_update_timestamp.get()
        current_time = SystemTime.get_current_time_in_ms()
        if current_time > next_cache_update:
            if self._next_cache_update_timestamp.compare_and_set(
                next_cache_update,
                current_time + self._cache_refresh_interval_in_ms,
            ):
                if self._client_registration_complete.get():
                    self._cached_experiments.set(
                        self._api_client.get_all_applicable_experiments()
                    )
                else:
                    self._cached_experiments.set(
                        self._api_client.register_client(
                            self._application_coordinates,
                            self._client_registration_complete,
                        )
                    )

    def determine_if_experiment_applies(
        self,
        map_from_api: dict[TrafficQuery, ExperimentImpact],
        coordinates: TrafficCoordinates,
    ) -> ExperimentImpact:
        customer_provided_coordinates = (
            self._gremlin_coordinates_provider.extend_each_traffic_coordinates(
                coordinates
            )
        )
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(
                f"Matching on Traffic Coordinates {customer_provided_coordinates}"
            )
        for traffic_query in map_from_api.keys():
            if logger.getEffectiveLevel() is logging.DEBUG:
                logger.debug(
                    f"Comparing customer coordinates against {traffic_query}"
                )
            if traffic_query.should_apply_impact(
                customer_provided_coordinates
            ):
                return map_from_api[traffic_query]
