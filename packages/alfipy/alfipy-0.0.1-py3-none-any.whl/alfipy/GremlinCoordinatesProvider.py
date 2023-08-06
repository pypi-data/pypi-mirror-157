# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import logging

from abc import ABCMeta, abstractmethod

from .AlfiConstants import logger_name
from .ApplicationCoordinates import ApplicationCoordinates

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinCoordinatesProvider(metaclass=ABCMeta):
    """
    This class is the way to tell Gremlin about the attributes you care about when creating attacks.

    The :meth:`initialize_coordinates` is invoked at the beginning of your application lifecycle.
    You can uniquely identify your application to Gremlin, and then use those attributes when scoping your attack.

    The :meth:`extend_each_traffic_coordinates` is invoked each time your application
    encounters a possible fault-injection point.  If you have a cross-cutting concern (like userId/deviceId), you may
    attach it to all :class:`TrafficCoordinates` using this.
    """

    @abstractmethod
    def initialize_coordinates(self) -> ApplicationCoordinates:
        """
        Identify the application to Gremlin.
        Each :class:ApplicationCoordinates must have a type :class:ApplicationType and a set of
        key-value pairs which uniquely identify the application

        :return: Initialized :class:ApplicationCoordinates
        """
        raise NotImplementedError("Method needs to implemented in subclass")

    def extend_each_traffic_coordinates(self, incoming_coordinates):
        """
        For every set of :class:TrafficCoordinates, extend the set of attributes.  Each added attribute is then
        available to match on when creating blast radius.

        Since this happens for each :class:TrafficCoordinates, this is a convenient way to tell Gremlin about
        pieces of data that are in every request (Ex: customer, country, device, etc)

        For example, if you add "CUSTOMER_ID" as a traffic attribute
        (via `coordinates.put("CUSTOMER_ID", myCustomerId)`),
        then you can use "CUSTOMER_ID" in the Gremlin UI to target attacks

        :param incoming_coordinates: key-value map describing the traffic
        :return: the updated coordinates
        """
        # no-op
        return incoming_coordinates
