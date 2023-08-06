# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConfig import AlfiConfig
from .AlfiConstants import logger_name
from .Exceptions import ALFIApiClientException
from .GremlinApiClient import GremlinApiClient

from typing import ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinApiClientResolver:
    """
    Try to resolve a valid instance of :ref:`GremlinApiClient` from a list of known implementations
    """

    API_CLIENTS: ClassVar[list] = [
        "GremlinApiRequestsClient",
        "GremlinApiUrllib3Client",
        "GremlinApiHttpClient",
    ]

    @classmethod
    def get_client(
        cls,
        alfi_config: AlfiConfig,
        gremlin_service_endpoint: str,
        gremlin_service_version: str,
        max_retries: int = 10,
    ) -> GremlinApiClient:
        for api_client_type in cls.API_CLIENTS:
            api_client = None
            try:
                api_client = cls.get_specific_client(
                    api_client_type,
                    alfi_config,
                    gremlin_service_endpoint,
                    gremlin_service_version,
                    max_retries,
                )
                return api_client
            except ModuleNotFoundError:
                logger.warning(
                    f"Cannot load module `{api_client}` trying next api client module"
                )
            except NotImplementedError:
                logger.warning(
                    f"Cannot load module `{api_client}` trying next api client module"
                )
            except ALFIApiClientException as e:
                error_msg = f"Received fatal exception `{e}` trying to load module {api_client}"
                logger.critical(error_msg)
                raise ALFIApiClientException(error_msg) from e
            finally:
                if api_client:
                    logger.info(f"Created api_client from `{api_client_type}`")

    @classmethod
    def get_specific_client(
        cls,
        api_client: str,
        alfi_config: AlfiConfig,
        gremlin_service_endpoint: str,
        gremlin_service_version: str,
        max_retries: int = 10,
    ) -> GremlinApiClient:
        if api_client not in cls.API_CLIENTS:
            raise ALFIApiClientException("Requested client does not exist")
        try:
            import importlib

            client = getattr(
                importlib.import_module(f".{api_client}", package=__package__),
                api_client,
            )
            return client(
                alfi_config,
                gremlin_service_endpoint,
                gremlin_service_version,
                max_retries,
            )
        except ModuleNotFoundError as e:
            error_msg = f"Requirements to load `{api_client}` missing"
            logger.info(error_msg)
            if api_client == cls.API_CLIENTS[-1]:
                raise ALFIApiClientException(error_msg) from e
            raise ModuleNotFoundError(error_msg) from e
        except NotImplementedError as e:
            error_msg = f"The requested module `{api_client}` is not implemented, please try another module"
            logger.info(error_msg)
            if api_client == cls.API_CLIENTS[-1]:
                raise ALFIApiClientException(error_msg) from e
            raise NotImplementedError(error_msg) from e
        except Exception as e:
            logger.critical(
                f"received error `{e}` when trying to import api client `{api_client}`"
            )
            raise ALFIApiClientException(
                f"Cannot import `{api_client}`"
            ) from e
