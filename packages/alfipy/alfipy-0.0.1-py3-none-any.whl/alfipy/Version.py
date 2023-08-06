# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import sys

from .AlfiConstants import VERSION

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Version:
    version: str = field(default=VERSION)
    python_version: str = field(default=sys.version)
