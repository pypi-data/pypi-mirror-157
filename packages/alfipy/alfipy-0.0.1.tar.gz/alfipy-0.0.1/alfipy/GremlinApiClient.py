# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""API Client for Gremlin ALFI Python"""

from __future__ import annotations

import logging

from .alfi_messages_pb2 import (
    ExperimentResponseList as ALFIMessages_ExperimentResponseList,
)

from .AlfiConfig import AlfiConfig
from .AlfiConstants import logger_name
from .ApplicationCoordinates import ApplicationCoordinates
from .Atomic import AtomicBoolean
from .Client import Client
from .Exceptions import ALFIConfigurationException
from .ExperimentImpact import ExperimentImpact
from .ExperimentResponse import ExperimentResponse
from .GremlinTime import SystemTime
from .TrafficQuery import TrafficQuery
from .Version import Version

from abc import ABCMeta, abstractmethod
from typing import ClassVar, Optional

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinApiClient(metaclass=ABCMeta):
    """
    Abstract implementation of the communication stream from the ALFI Client to the Gremlin Control Plane
    """

    GREMLIN_AUTH_HEADER_NAME: ClassVar[str] = "Authorization"
    GREMLIN_AGENT_HEADER_NAME: ClassVar[str] = "X-Gremlin-Agent"
    GREMLIN_ALFI_PYTHON_AGENT_VALUE: ClassVar[str] = "alfi-python"
    CONTENT_TYPE_HEADER_NAME: ClassVar[str] = "Content-Type"
    PROTO_CONTENT_TYPE: ClassVar[str] = "application/protobuf"
    CONTENT_LENGTH_HEADER_NAME: ClassVar[str] = "Content-Length"
    VERSION: ClassVar[str] = Version.version
    RUNTIME: ClassVar[str] = "PYTHON"
    RUNTIME_VERSION: ClassVar[str] = Version.python_version

    DEFAULT_CONNECT_TIMEOUT_IN_MS: ClassVar[int] = 500
    DEFAULT_READ_TIMEOUT_IN_MS: ClassVar[int] = 2000

    def __init__(
        self,
        alfi_config: AlfiConfig,
        gremlin_service_endpoint: str,
        gremlin_service_version: str,
        max_retries: int = 10,
    ) -> None:
        self._alfi_config = alfi_config
        self._gremlin_service_endpoint = gremlin_service_endpoint
        self._gremlin_service_version = gremlin_service_version
        self._max_retries = max_retries
        self._http_conn = None
        self._initialize_conn()

    @abstractmethod
    def _initialize_conn(self) -> None:
        raise NotImplementedError("Method needs to implemented in subclass")

    def _build_headers(self, content_length: Optional[int] = None) -> dict:
        headers = {
            self.GREMLIN_AUTH_HEADER_NAME: f"{self._alfi_config.auth_header_value}",
            self.GREMLIN_AGENT_HEADER_NAME: f"{self.GREMLIN_ALFI_PYTHON_AGENT_VALUE}/{self.VERSION}",
            "Connection": "keep-alive",
        }
        if content_length and type(content_length) is int:
            headers[self.CONTENT_LENGTH_HEADER_NAME] = content_length
            headers[self.CONTENT_TYPE_HEADER_NAME] = self.PROTO_CONTENT_TYPE
        return headers

    @abstractmethod
    def _request(
        self,
        method: str = None,
        url: str = None,
        body: str = None,
        headers: dict = None,
        retry: int = 0,
    ) -> dict:
        raise NotImplementedError("Method needs to implemented in subclass")

    @SystemTime.measure_execution_time
    def get_all_applicable_experiments(
        self,
    ) -> dict[TrafficQuery, ExperimentImpact]:
        start_time = SystemTime.get_current_time_in_ms()
        if not self._alfi_config.client_identifier:
            error_msg = "Cannot retreive experiments without client identifier"
            logger.critical(error_msg)
            raise ALFIConfigurationException(error_msg)
        endpoint = f"/experiments/{self._alfi_config.client_identifier}"
        headers = self._build_headers()
        experiments_response = self._request("GET", endpoint, headers=headers)
        experiments = {}
        if 200 <= experiments_response.get("status") <= 300:
            experiments = self.handle_experiments(experiments_response["data"])
            if logger.getEffectiveLevel() is logging.DEBUG:
                logger.debug(
                    f"Received Gremlin API Experiments({len(experiments.items())}) "
                    + f"took {SystemTime.get_current_time_in_ms() - start_time} ms"
                )
        else:
            logger.warning(
                f'Failed to get experiments, received {experiments_response.get("status")} status code '
                + f'error: {experiments_response.get("error")}'
            )
        return experiments

    @SystemTime.measure_execution_time
    def register_client(
        self,
        application_coordinates: ApplicationCoordinates,
        client_registration_complete: AtomicBoolean,
    ) -> dict[TrafficQuery, ExperimentImpact]:
        start_time = SystemTime.get_current_time_in_ms()
        client = Client(
            application_coordinates,
            self._alfi_config.client_identifier,
            self.RUNTIME,
            self.RUNTIME_VERSION,
        )
        client_msg = client.to_message()
        headers = self._build_headers(content_length=client_msg.ByteSize())
        experiments_response = self._request(
            "POST",
            "/alfi/clients",
            client_msg.SerializeToString(),
            headers=headers,
        )
        experiments = {}
        if 200 <= experiments_response.get("status") <= 300:
            experiments = self.handle_experiments(experiments_response["data"])
            client_registration_complete.set(True)
            if logger.getEffectiveLevel() is logging.DEBUG:
                logger.debug(
                    f"Received Gremlin API Experiments({len(experiments.items())}) "
                    + f"took {SystemTime.get_current_time_in_ms() - start_time} ms"
                )
        else:
            logger.warning(
                f'Failed to register client, received {experiments_response.get("status")} status code '
                + f'error: {experiments_response.get("error")}'
            )
        return experiments

    @SystemTime.measure_execution_time
    def mark_impact(self, experiment_guid: str) -> None:
        start_time = SystemTime.get_current_time_in_ms()
        if not self._alfi_config.client_identifier:
            error_msg = (
                "Cannot mark experiment impact without client identifier"
            )
            logger.critical(error_msg)
            raise ALFIConfigurationException(error_msg)
        endpoint = f"/experiments/{experiment_guid}/Impacted/{self._alfi_config.client_identifier}"
        headers = self._build_headers()
        impact_response = self._request("POST", endpoint, headers=headers)
        if 200 <= impact_response.get("status") <= 300:
            logger.info(
                f"Marked Impact {self._alfi_config.client_identifier} {experiment_guid} "
                + f"took {SystemTime.get_current_time_in_ms() - start_time} ms"
            )
        else:
            logger.critical(
                f'Failed to mark impact, received {impact_response.get("status")} error code '
                + f'with {impact_response.get("error")} error'
            )

    def handle_experiments(
        self, response
    ) -> dict[TrafficQuery, ExperimentImpact]:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(f"received experiment response: {response}")
        response_as_map = {}
        if len(response) > 0:
            binary_response = bytearray()
            binary_response.extend(response)
            response_message = ALFIMessages_ExperimentResponseList()
            response_message.ParseFromString(binary_response)
            responses = ExperimentResponse.list_from_message(response_message)
            for experiment in responses:
                for query_and_impact in experiment.traffic:
                    failure = ExperimentImpact.parse_from_impact(
                        guid=experiment.guid, impact=query_and_impact.impact
                    )
                    response_as_map[query_and_impact.query] = failure
        else:
            logger.info("no experiments to handle")
        return response_as_map

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError("Method needs to implemented in subclass")
