# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentVariableNameKeys:
    """
    A static mapping of the environment variables ALFI will look for
    """

    gremlin_application_type = "GREMLIN_APPLICATION_TYPE"
    gremlin_application_labels = "GREMLIN_APPLICATION_LABELS"
    gremlin_identifier = "GREMLIN_ALFI_IDENTIFIER"
    gremlin_team_id = "GREMLIN_ALFI_TEAM_ID"
    cache_interval_in_ms = "GREMLIN_ALFI_CACHE_INTERVAL_IN_MS"
    http_proxy = "HTTP_PROXY"
    certificate_or_file_reference = "GREMLIN_ALFI_CERTIFICATE_OR_FILE"
    private_key_or_file_reference = "GREMLIN_ALFI_PRIVATE_KEY_OR_FILE"
