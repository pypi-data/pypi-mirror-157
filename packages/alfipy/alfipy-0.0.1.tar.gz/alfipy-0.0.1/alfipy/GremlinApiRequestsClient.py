# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""API Client for Gremlin ALFI Python"""

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .GremlinApiClient import GremlinApiClient


logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinApiRequestsClient(GremlinApiClient):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This module is not yet implemented")

    def _initialize_conn(self) -> None:
        pass

    def _request(
        self,
        method: str = None,
        url: str = None,
        body: str = None,
        headers: dict = None,
        retry: int = 0,
    ) -> dict:
        pass

    def shutdown(self) -> None:
        pass
