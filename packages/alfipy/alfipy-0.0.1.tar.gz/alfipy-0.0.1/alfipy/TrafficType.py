# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

from .TypedAlfiModel import TypedAlfiModel

from dataclasses import dataclass


@dataclass(frozen=True)
class TrafficType(TypedAlfiModel.Type):
    """
    Passthrough object to map `traffic.type` into the type structured data model
    """

    def __post_init__(self):
        pass
