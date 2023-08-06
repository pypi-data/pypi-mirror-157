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
from alfipy.alfipy.GremlinServiceFactory import GremlinServiceFactory
from alfipy.alfipy.GremlinConfigurationResolver import (
    GremlinConfigurationResolver,
)
from alfipy.alfipy.GremlinCoordinatesProvider import GremlinCoordinatesProvider
from alfipy.alfipy.PassthroughGremlinService import PassthroughGremlinService

log = logging.getLogger(f"{logger_name}.{__name__}")
log.setLevel(logging.DEBUG)


class TestGremlinServiceFactory(unittest.TestCase):
    def test___new__(self) -> None:
        helper = GremlinServiceFactory(
            GremlinCoordinatesProvider, GremlinConfigurationResolver
        )
        helper_instance = GremlinServiceFactory.__new__(
            GremlinServiceFactory,
            GremlinCoordinatesProvider,
            GremlinConfigurationResolver,
        )
        self.assertEqual(helper, helper_instance)
        self.assertTrue(isinstance(helper, GremlinServiceFactory))
        self.assertTrue(isinstance(helper_instance, GremlinServiceFactory))

    def test_get_gremlin_service(self) -> None:
        helper = helper = GremlinServiceFactory(
            GremlinCoordinatesProvider, GremlinConfigurationResolver
        )
        expected_return = PassthroughGremlinService()
        self.assertEqual(helper.get_gremlin_service(), expected_return)
