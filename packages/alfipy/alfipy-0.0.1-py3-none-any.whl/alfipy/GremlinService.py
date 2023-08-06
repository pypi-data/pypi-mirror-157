# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .AlfiConstants import AlfiConstants, logger_name
from .Exceptions import ALFIIntentionalException
from .ExperimentImpact import ExperimentImpact
from .GremlinTime import GremlinTime, SystemTime
from .TrafficCoordinates import TrafficCoordinates

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinService(metaclass=ABCMeta):
    """
    High-level orchestration of calls to Gremlin API.  This provides a buffer between accessing
    experiments for Traffic Coordinates :meth:`get_experiment(:ref:`TrafficCoordinates`)` and
    actual calls to the Gremlin API

    A user obtains an instance of :ref:`GremlinService` by invoking
    :ref:`GremlinServiceFactory`:meth:`get_gremlin_service()`

    The :ref:`GremlinServiceFacotry` accepts :ref:`GremlinCoordinatesProvider` and
    :ref:`GremlinConfigurationResolver` as arguments, so those may be supplied if that functionality
    needs to be overridden.

    The :ref:`GremlinService` is used in the injection points created by the user.
    It's an argument to the Gremlin-provided injection points, and also has methods like
    :ref:`GremlinService`:meth:`execute(TrafficCoordinates, Runnable)` and
    :ref:`GremlinService`:meth:`execute(TrafficCoordinates, Supplier)` to wrap arbitrary
    units of work in fault-injection.
    """

    _instance = None

    def __init__(self):
        pass

    @abstractmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GremlinService, cls).__new__(cls)
        return cls._instance

    def try_inject_impact(self, clazz: str, method: str) -> None:
        if not self.has_experiments():
            return

        coordinates = TrafficCoordinates()

        self.apply_impact(coordinates, GremlinTime.system())

    @abstractmethod
    def has_experiments(self) -> bool:
        """
        Determine if any experiments are currently cached.
        :return: bool
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @abstractmethod
    def get_experiment(
        self, traffic_coordinates: TrafficCoordinates
    ) -> ExperimentImpact:
        """
        Given a specific injection point ({@link TrafficCoordinates}), find an impact to inject, if applicable.
        Is subject to some latency, as reading experiments requires calls to API
        :param traffic_coordinates:
        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown all Gremlin resources
        :return:
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    def apply_impact(
        self,
        traffic_coordinates: TrafficCoordinates,
        time: GremlinTime = SystemTime(),
    ) -> None:
        impact_from_service = self.get_experiment(traffic_coordinates)
        if impact_from_service:
            found_impact = impact_from_service.impact
            latency_to_add_in_ms = found_impact.get_impact_parameter(
                AlfiConstants.KEY_LATENCY_TO_ADD_IN_MS
            )
            throw_exception = found_impact.get_impact_parameter(
                AlfiConstants.KEY_EXCEPTION_SHOULD_BE_THROWN
            )

            logger.info(
                f"Gremlin injecting {found_impact} for : {traffic_coordinates}"
            )

            if latency_to_add_in_ms > 0:
                time.advance_millis(latency_to_add_in_ms)
            if throw_exception:
                raise ALFIIntentionalException(
                    AlfiConstants.FAULT_INJECTED_MESSAGE
                )
