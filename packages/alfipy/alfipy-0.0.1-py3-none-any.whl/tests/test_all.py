# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import unittest

from .test_config import TestConfig
from .test_config_wkeys import TestAlfiConfigFromCertificateAndPrivateKey
from .test_api_gremlin_service import (
    TestApiGremlinService,
)  # needs either elimination or cross referencing from java unit tests
from .test_application_coordinates import TestApplicationCoordinates
from .test_atomic import TestAtomic
from .test_bounded_concurrent_set import TestBoundedConcurrentSet
from .test_client import TestClient
from .test_coordinates import TestCoordinates
from .test_env_variable_coordinates_provider import (
    TestEnvironmentVariableCoordinatesProvider,
)
from .test_exact_field import TestExactField
from .test_experiment_impact import TestExperimentImpact
from .test_experiment_response import TestExperimentResponse
from .test_gremlin_alfi_crypto import TestGremlinALFICrypto
from .test_gremlin_api_client_factory import TestGremlinApiClientFactory
from .test_gremlin_api_client_resolver import TestGremlinApiClientResolver
from .test_gremlin_api_http_client import TestGremlinApiHttpClient
from .test_gremlin_interceptor import TestGremlinInterceptor
from .test_gremlin_service_factory import TestGremlinServiceFactory
from .test_gremlin_time import TestGremlinTime
from .test_impact import TestImpact
from .test_impact_provider import TestImpactProvider
from .test_query_field import TestQueryField
from .test_traffic_and_impact_provider import TestTrafficAndImpactProvider
from .test_traffic_coordinates import TestTrafficCoordinates
from .test_traffic_query import TestTrafficQuery
from .test_traffic_query_and_impact import TestTrafficQueryAndImpact
from .test_traffic_query_provider import TestTrafficQueryProvider
from .test_wildcard_field import TestWildcardField

if __name__ == "__main__":
    unittest.main()
