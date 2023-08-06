# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import functools
import inspect
import logging

from .AlfiConstants import logger_name
from .Exceptions import ALFIConfigurationException
from .EnvironmentVariableCoordinatesProvider import (
    EnvironmentVariableCoordinatesProvider,
)
from .ExperimentImpact import ExperimentImpact
from .GremlinConfigurationResolver import GremlinConfigurationResolver
from .GremlinCoordinatesProvider import GremlinCoordinatesProvider
from .GremlinServiceFactory import GremlinServiceFactory
from .TrafficCoordinates import TrafficCoordinates

from typing import Callable

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinInterceptor:
    """
    This is the default interceptor that can be used for basic implementations of ALFI

    Examples:
        class MyMath(object):
          @GremlinInterceptor.gremlin_attack(type=__class__.__name__, fields={'method': 'add2'})
          def add2(x: int=None, y: int=None):
            return x + y
    """

    _instance = None

    def __init__(
        self,
        configuration_resolver: GremlinConfigurationResolver = GremlinConfigurationResolver,
        coordinates_provider: GremlinCoordinatesProvider = EnvironmentVariableCoordinatesProvider,
        service_factory: GremlinServiceFactory = GremlinServiceFactory,
    ):
        self._configuration_resolver = configuration_resolver
        self._coordinates_provider = coordinates_provider
        self._service_factory = service_factory
        self.service = self._service_factory(
            self._coordinates_provider(), self._configuration_resolver()
        ).get_gremlin_service()

    def __new__(
        cls,
        configuration_resolver: GremlinConfigurationResolver = GremlinConfigurationResolver,
        coordinates_provider: GremlinCoordinatesProvider = EnvironmentVariableCoordinatesProvider,
        service_factory: GremlinServiceFactory = GremlinServiceFactory,
    ):
        if cls._instance is None:
            cls._instance = super(GremlinInterceptor, cls).__new__(cls)
            # cls._instance = super(GremlinInterceptor, cls).__new__(
            #     cls,
            #     configuration_resolver,
            #     coordinates_provider,
            #     service_factory,
            # )
        return cls._instance

    def build_coordinates(
        self,
        func: Callable,
        args: list,
        kwargs: dict,
        type: str,
        fields: dict = {},
    ) -> TrafficCoordinates:
        """
        Builds the metadata fields to pass to the coordinates provider

        By default, this inspects all information passed to the function
        and automatically coerce elements into strings and turn them
        into traffic coordinates.

        :param func:
        :param args:
        :param kwargs:
        :param type:
        :param fields:
        :return:
        """
        coordinates_builder = TrafficCoordinates.Builder().with_type(type)
        signature_args = []
        signature_vararg = None
        signature_keywords = []
        signature_defaults = {}
        try:
            signature = inspect.signature(func)
            for param in signature.parameters.values():
                name = param.name
                kind = param.kind
                if kind is inspect.Parameter.POSITIONAL_ONLY:
                    signature_args.append(name)
                    if param.default is not param.empty:
                        signature_defaults[name] = param.default
                elif kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    signature_args.append(name)
                    if param.default is not param.empty:
                        signature_defaults[name] = param.default
                elif kind is inspect.Parameter.VAR_POSITIONAL:
                    signature_vararg = name
                elif kind is inspect.Parameter.KEYWORD_ONLY:
                    signature_keywords.append(name)
                    if param.default is not param.empty:
                        signature_defaults[name] = param.default
            if signature_args or signature_vararg:
                for idx, arg in enumerate(args):
                    if str(arg):
                        try:
                            if str(signature_args[idx]) and str(arg):
                                coordinates_builder.with_field(
                                    str(signature_args[idx]), str(arg)
                                )
                        except IndexError:
                            if signature_vararg and str(signature_vararg):
                                coordinates_builder.with_field(
                                    f"{str(signature_vararg)}{str(idx)}",
                                    str(arg),
                                )
            if kwargs:
                for k, v in kwargs.items():
                    if str(k) and str(v):
                        coordinates_builder.with_field(str(k), str(v))
            if fields:
                for k, v in fields.items():
                    if str(k) and str(v):
                        coordinates_builder.with_field(str(k), str(v))
        except Exception as ex:
            logger.critical(f"Encountered critical failure: {ex}")
            raise Exception from ex
        return coordinates_builder.build()

    def coordinates(self, type: str = None, fields: dict = None):
        """
        The main wrapper to apply impact against targeted methods

        Args:
            :param type: Type classification, commonly class name
            :param fields: Optional targeting metadata

        Returns:
            None
        """
        if not type:
            error_msg = "Type is a required field"
            logger.critical(error_msg)
            raise ALFIConfigurationException(error_msg)
        if not fields:
            fields = {}

        def coordinates_wrapper(func):
            @functools.wraps(func)
            def coordinates_wrapper_inner(*args, **kwargs):
                if self.service.has_experiments():
                    self.service.apply_impact(
                        self.build_coordinates(
                            func, args, kwargs, type, fields
                        )
                    )
                return func(*args, **kwargs)

            return coordinates_wrapper_inner

        return coordinates_wrapper
