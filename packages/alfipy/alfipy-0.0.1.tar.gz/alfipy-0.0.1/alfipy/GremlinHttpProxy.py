# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import logging

from .AlfiConstants import logger_name

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinHttpProxy(object):
    DEFAULT_PROXY_PORT = 80

    def __init__(self) -> None:
        pass
