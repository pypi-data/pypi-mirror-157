# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .GremlinHttpProxy import GremlinHttpProxy

from dataclasses import dataclass, field


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class GremlinConfiguration:
    """
    Configuration Object used by ALFI
    """

    gremlin_identifier: str = field(default="")
    gremlin_team_id: str = field(default="")
    cache_interval_in_ms: int = field(default="")
    http_proxy: GremlinHttpProxy = field(default="")
    certificate_or_file_reference: str = field(default="")
    private_key_or_file_reference: str = field(default="")
