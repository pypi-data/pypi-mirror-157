# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import http.client
import logging

from .AlfiConstants import logger_name
from .GremlinApiClient import GremlinApiClient

from http.client import CannotSendRequest
from time import sleep

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinApiHttpClient(GremlinApiClient):
    """
    Basic implementation :ref:`GremlinApiClient` using python built-in `http.client` library for API interaction

    This library is _*NOT*_ thread-safe
    This library is _*NOT TESTED*_ for python multiprocess safety
    """

    def _initialize_conn(self) -> None:
        if self._http_conn:
            if logger.getEffectiveLevel() is logging.DEBUG:
                logger.debug(
                    "http connection exists, trying to close existing http connection"
                )
            self._http_conn.close()
            del self._http_conn
        self._http_conn = self._build_conn()

    def _build_conn(self) -> object:
        # REFACTOR!
        # To handle a proxy, the logic needs to be:
        # IF PROXY_VAR:
        #   http_client = http.client.HTTPSConnection( PROXY_HOST, PROXY_PORT )
        #   http_client.set_tunnel( self._gremlin_service_endpoint )
        #   return http_client
        # ELSE:
        return http.client.HTTPSConnection(
            self._gremlin_service_endpoint,
            timeout=self.DEFAULT_CONNECT_TIMEOUT_IN_MS / 1000,
        )

    def _request(
        self,
        method: str = None,
        url: str = None,
        body: str = None,
        headers: dict = None,
        retry: int = 0,
    ) -> dict:
        # if body:
        #     self._http_conn.request(method, f'{url}', body, headers=headers)
        # else:
        #     self._http_conn.request(method, f'{url}', headers=headers)
        self._http_conn.request(
            method,
            f"{self._gremlin_service_version}{url}",
            body,
            headers=headers,
        )
        try:
            response = self._http_conn.getresponse()
        except CannotSendRequest as e:
            logger.critical(f"CannotSendRequest: {e}")
            if retry <= self._max_retries:
                if logger.getEffectiveLevel() is logging.DEBUG:
                    logger.debug(
                        f"Retry {retry} of {self._max_retries}:"
                        + f"Waiting {retry} seconds and retrying request to {url}"
                    )
                sleep(retry)
                self._initialize_conn()
                return self._request(method, url, body, headers, retry + 1)
            else:
                logger.critical(
                    f"exceeded maximum retries of {self._max_retries} for request to {url} ;;"
                    + f"returning error {e}"
                )
                return {"status": -1, "error": e}
        except Exception as e:
            logger.critical(f"ConnectionError: {e}")
            if retry <= self._max_retries:
                if logger.getEffectiveLevel() is logging.DEBUG:
                    logger.debug(
                        f"Retry {retry} of {self._max_retries}:"
                        + f"Waiting {retry} seconds and retrying request to {url}"
                    )
                sleep(retry)
                self._initialize_conn()
                return self._request(method, url, body, headers, retry + 1)
            else:
                logger.critical(
                    f"exceeded maximum retries of {self._max_retries} for request to {url} ;;"
                    + f"returning error {e}"
                )
                return {"status": -1, "error": e}
        if 200 <= response.status <= 399:
            return {
                "data": response.read(),
                "status": response.status,
                "headers": response.getheaders(),
                "raw": response,
            }
        elif 400 <= response.status <= 499:
            logger.critical(
                f"Received {response.status} error code, initiating retry {retry} of {self._max_retries}"
            )
            self._http_conn.close()
            if retry <= self._max_retries:
                return self._request(method, url, body, headers, retry + 1)
            else:
                logger.critical(
                    f"exceeded maximum retries of {self._max_retries} for request to {url}"
                )
                return {"status": -1}
        else:
            return {"status": response.status}

    def shutdown(self) -> None:
        self._http_conn.close()
