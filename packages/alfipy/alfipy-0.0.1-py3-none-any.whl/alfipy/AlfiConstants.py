# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""
This provides a module-wide set of static information
"""

from __future__ import annotations

import re

from dataclasses import dataclass

VERSION = "0.0.1"

logger_name = "GremlinALFI.client"

service_endpoint = "beta.gremlin.com"

service_version = "/v1"

service_url = service_endpoint + "/" + service_version

CERTIFICATE_PREAMBLE = "-----BEGIN CERTIFICATE-----"
CERTIFICATE_POSTAMBLE = "-----END CERTIFICATE-----"
PRIVATE_KEY_PREAMBLE = "-----BEGIN EC PRIVATE KEY-----"
PRIVATE_KEY_POSTAMBLE = "-----END EC PRIVATE KEY-----"

GREMLIN_AUTH_HEADER_PREFIX = "ALFI"
FILE_PREFIX = "file://"
REPLACE_LITERAL_SLASH_N = re.compile("\\n")


@dataclass(frozen=True)
class AlfiConstants:
    from .QueryModel import QueryModel
    from .TypedAlfiModel import TypedAlfiModel

    # Messages
    FAULT_INJECTED_MESSAGE: str = "Fault injected by Gremlin"

    # Type Names
    AQ_AWS_LAMBDA_NAME: str = "AwsLambda"
    AQ_AWS_EC2_NAME: str = "AwsEc2"
    TQ_OUTBOUND_HTTP_NAME: str = "OutboundHttp"
    TQ_INBOUND_HTTP_NAME: str = "InboundHttp"
    TQ_AWS_DYNAMO_NAME: str = "AwsDynamo"
    TQ_METHOD_NAME: str = "PythonMethod"
    TQ_UNMATCHABLE_NAME: str = "Unmatchable"
    TI_GENERAL_NAME: str = "General"

    # Shared Keys
    KEY_REGION: str = "region"
    KEY_AVAILABILITY_ZONE: str = "az"
    KEY_INSTANCE_ID: str = "instance_id"
    KEY_LAMBDA_NAME: str = "name"

    KEY_VERB: str = "verb"
    KEY_CLIENT_NAME: str = "client_name"
    KEY_PATH: str = "path"

    KEY_TABLE: str = "table"
    KEY_OPERATION: str = "operation"

    KEY_CLASS: str = "class"
    KEY_METHOD: str = "method"

    KEY_LATENCY_TO_ADD_IN_MS: str = "latency_to_add_in_ms"
    KEY_EXCEPTION_SHOULD_BE_THROWN: str = "exception_should_be_thrown"

    # Query Keys
    AQ_KEYS_AWS_LAMBDA: TypedAlfiModel.Keys = (
        TypedAlfiModel.Keys().required(KEY_REGION).required(KEY_LAMBDA_NAME)
    )

    AQ_KEYS_AWS_EC2: TypedAlfiModel.Keys = (
        TypedAlfiModel.Keys()
        .required(KEY_REGION)
        .required(KEY_AVAILABILITY_ZONE)
        .required(KEY_INSTANCE_ID)
    )

    TQ_KEYS_HTTP: TypedAlfiModel.Keys = (
        TypedAlfiModel.Keys().required(KEY_VERB).required(KEY_CLIENT_NAME)
    )

    TQ_KEYS_INBOUND_HTTP: TypedAlfiModel.Keys = TypedAlfiModel.Keys().required(
        KEY_VERB
    )

    TQ_KEYS_AWS_DYNAMO: TypedAlfiModel.Keys = (
        TypedAlfiModel.Keys()
        .optional(KEY_REGION)
        .required(KEY_TABLE)
        .required(KEY_OPERATION)
    )

    TQ_KEYS_METHOD: TypedAlfiModel.Keys = (
        QueryModel.Keys().required(KEY_CLASS).required(KEY_METHOD)
    )

    TI_KEYS_GENERAL: TypedAlfiModel.Keys = (
        TypedAlfiModel.Keys()
        .required(KEY_LATENCY_TO_ADD_IN_MS)
        .required(KEY_EXCEPTION_SHOULD_BE_THROWN)
    )
