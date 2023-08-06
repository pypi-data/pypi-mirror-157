# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod
from .AlfiConstants import logger_name


logger = logging.getLogger(f"{logger_name}.{__name__}")


class EnvironmentVariableProvider(metaclass=ABCMeta):
    """
    Skeleton to extend dynamic environment variable getters from ;; future work
    """

    pass
