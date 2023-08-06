# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging

from abc import ABCMeta, abstractmethod

from .AlfiConfig import AlfiConfig
from .AlfiConstants import logger_name
from .AlfiConfigFromCertificateAndPrivateKey import (
    AlfiConfigFromCertificateAndPrivateKey,
)
from .GremlinConfiguration import GremlinConfiguration

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinConfigurationResolver(metaclass=ABCMeta):
    """
    An interface that you can implement if you want to supply a :class:GremlinConfiguration when setting up Gremlin.
    If you choose not to, then Gremlin will look for these values in `gremlin.properties` and environment-variables
    """

    @classmethod
    @abstractmethod
    def get_config(cls) -> GremlinConfiguration:
        """
        Supply config values as a set of strings
        This method may be implemented outside of this library, so we need to eagerly resolve all values it contains
        to check for errors, before we start using it

        :return: :class:GremlinConfiguration: The configuration values
        """
        raise NotImplementedError(
            "This method needs to be implemented in a subclass"
        )

    @classmethod
    def get_resolved_config(cls) -> AlfiConfig:
        """
        Expectation is that `getConfig` returns a full `GremlinConfiguration` object - possibly via
        `:class:SystemGremlinConfigurationResolver`, possibly via a user-defined method.
        In either case, use those values to eagerly set up all of the necessary configuration objects and
        verify they are present and valid.

        :return: :class:AlfiConfig: config object if all pieces are validated
        """
        logger.info(f"Gremlin ALFI is looking up configuration using {cls}")
        c = cls.get_config()
        return AlfiConfigFromCertificateAndPrivateKey(
            client_identifier=c.gremlin_identifier,
            gremlin_team_id=c.gremlin_team_id,
            cache_interval_in_ms=c.cache_interval_in_ms,
            http_proxy=c.http_proxy,
            raw_certificate_or_reference=c.certificate_or_file_reference,
            raw_private_key_or_reference=c.private_key_or_file_reference,
        )
