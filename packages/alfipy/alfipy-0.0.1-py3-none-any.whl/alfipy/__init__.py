# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""
:mod:`alfipy` -- Gremlin Application Layer Fault Injection, Python Edition
==========================================================================

.. module:: alfipy
    :platform: Linux
    :synopsis: Inject fault into your application layer
"""

import logging
import os

from .AlfiConstants import logger_name, VERSION


__version__ = VERSION


logging_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}

logger = logging.getLogger(logger_name)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
)
log_handler.setFormatter(log_formatter)
# log.addFilter(SecretsFilter())
logger.addHandler(log_handler)
logger.setLevel(
    logging_levels.get(
        os.getenv("GREMLIN_PYTHON_API_LOG_LEVEL", "WARNING"), logging.WARNING
    )
)
