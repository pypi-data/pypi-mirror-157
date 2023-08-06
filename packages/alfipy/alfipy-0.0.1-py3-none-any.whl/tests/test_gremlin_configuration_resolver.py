# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest
from unittest.mock import patch
import logging

# import requests

from alfipy.alfipy.AlfiConstants import logger_name
from alfipy.alfipy.GremlinConfigurationResolver import (
    GremlinConfigurationResolver,
)
from alfipy.alfipy.GremlinConfiguration import GremlinConfiguration
from alfipy.alfipy.GremlinHttpProxy import GremlinHttpProxy
from alfipy.alfipy.AlfiConfigFromCertificateAndPrivateKey import (
    AlfiConfigFromCertificateAndPrivateKey,
)

from .util import mock_identifier, mock_teamid, cert_filename, privk_filename

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinConfigurationResolver(unittest.TestCase):
    # @patch("alfipy.alfipy.GremlinConfiguration.get_config")
    def test_get_resolved_config(self) -> None:
        interval = 1000
        proxy = GremlinHttpProxy()
        GremlinConfiguration.client_identifier = mock_identifier
        GremlinConfiguration.gremlin_team_id = mock_teamid
        GremlinConfiguration.cache_interval_in_ms = interval
        GremlinConfiguration.http_proxy = proxy
        GremlinConfiguration.raw_certificate_or_reference = cert_filename
        GremlinConfiguration.raw_private_key_or_reference = privk_filename

        expected_output = AlfiConfigFromCertificateAndPrivateKey(
            client_identifier=mock_identifier,
            gremlin_team_id=mock_teamid,
            cache_interval_in_ms=interval,
            http_proxy=proxy,
            raw_certificate_or_reference=cert_filename,
            raw_private_key_or_reference=privk_filename,
        )

        # NotImplementedError: This method needs to be implemented in a subclass (get_config())
        self.assertEqual(
            expected_output, GremlinConfigurationResolver.get_resolved_config()
        )
