# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from .AlfiConstants import logger_name
from .TypedAlfiModel import TypedAlfiModel

from dataclasses import dataclass


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass(frozen=True)
class ImpactType(TypedAlfiModel.Type):
    """
    Passthrough object to map `impact.type` into the type structured data model
    """

    pass
