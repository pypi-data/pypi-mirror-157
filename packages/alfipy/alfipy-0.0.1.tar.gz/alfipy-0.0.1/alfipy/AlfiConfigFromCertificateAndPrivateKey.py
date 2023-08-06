# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import logging
import os.path as path

from .AlfiConfig import AlfiConfig
from .AlfiConstants import (
    logger_name,
    CERTIFICATE_PREAMBLE,
    CERTIFICATE_POSTAMBLE,
    FILE_PREFIX,
    GREMLIN_AUTH_HEADER_PREFIX,
    PRIVATE_KEY_PREAMBLE,
    PRIVATE_KEY_POSTAMBLE,
    REPLACE_LITERAL_SLASH_N,
)
from .Exceptions import (
    ALFICertificateException,
    ALFIConfigurationException,
    ALFIFileNotFoundException,
    ALFIPrivateKeyException,
)
from .GremlinALFICrypto import GremlinALFICrypto
from .GremlinHttpProxy import GremlinHttpProxy

from dataclasses import dataclass, field
from typing import ClassVar


logger = logging.getLogger(f"{logger_name}.{__name__}")


@dataclass
class AlfiConfigFromCertificateAndPrivateKey(AlfiConfig):
    """
    Implementation of the :ref:`AlfiConfig` interface
    """

    http_proxy: GremlinHttpProxy = field(default=GremlinHttpProxy())
    raw_certificate_or_reference: str = field(default="")
    raw_private_key_or_reference: str = field(default="")

    def __post_init__(self) -> None:
        self._certificate: str = ""
        self._private_key: str = ""

    @property
    def auth_header_value(self) -> str:
        signature = GremlinALFICrypto.build_signature(
            self.gremlin_team_id, self.certificate, self.private_key
        )
        return f"{GREMLIN_AUTH_HEADER_PREFIX} {signature}"

    @property
    def certificate(self) -> str:
        if not self._certificate:
            self._certificate = self.resolve_certificate(
                self.raw_certificate_or_reference
            )
        return self._certificate

    @property
    def private_key(self) -> str:
        if not self._private_key:
            self._private_key = self.resolve_private_key(
                self.raw_private_key_or_reference
            )
        return self._private_key

    @classmethod
    def resolve_certificate(
        cls, raw_certificate_or_file_reference: str
    ) -> str:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(
                f"Trying to resolve {raw_certificate_or_file_reference} to a valid certificate"
            )
        if (
            raw_certificate_or_file_reference == CERTIFICATE_PREAMBLE
            or raw_certificate_or_file_reference.startswith(
                f"{CERTIFICATE_PREAMBLE} "
            )
        ):
            error_msg = (
                "Gremlin ALFI certificate not readable due to newlines.  "
                'Please format the certificate with literal "\n" in place of the newlines'
            )
            logger.critical(error_msg)
            raise ALFICertificateException(error_msg)
        if raw_certificate_or_file_reference.startswith(FILE_PREFIX):
            certificate_pem = raw_certificate_or_file_reference.replace(
                FILE_PREFIX, ""
            )
            if path.exists(certificate_pem) and path.isfile(certificate_pem):
                try:
                    with open(certificate_pem, "r") as certificateHandler:
                        resolved_certificate = certificateHandler.read()
                except Exception as e:
                    error_msg = f"Could not read Gremlin ALFI certificate at: {raw_certificate_or_file_reference}"
                    logger.critical(error_msg)
                    raise ALFICertificateException(error_msg) from e
            else:
                error_msg = f"Could not find Gremlin ALFI certificate at: {raw_certificate_or_file_reference}"
                logger.critical(error_msg)
                raise ALFIFileNotFoundException(error_msg)
        else:
            resolved_certificate = raw_certificate_or_file_reference
        if GremlinALFICrypto.is_base64_encoded_certificate_or_private_key(
            resolved_certificate
        ):
            return resolved_certificate
        else:
            error_msg = (
                "Certificate does not resolve to a valid Base64 encoded string"
            )
            logger.critical(error_msg)
            raise ALFICertificateException(error_msg)

    @classmethod
    def resolve_private_key(
        cls, raw_private_key_or_file_reference: str
    ) -> str:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(
                f"Trying to resolve {raw_private_key_or_file_reference} to a valid key"
            )
        if (
            raw_private_key_or_file_reference == PRIVATE_KEY_PREAMBLE
            or raw_private_key_or_file_reference.startswith(
                f"{PRIVATE_KEY_PREAMBLE} "
            )
        ):
            error_msg = (
                "Gremlin ALFI private key not readable due to newlines. "
                + 'Please format the private key with literal "\n" in place of newlines'
            )
            logger.critical(error_msg)
            raise ALFIPrivateKeyException(error_msg)
        if raw_private_key_or_file_reference.startswith(FILE_PREFIX):
            private_key_pem = raw_private_key_or_file_reference.replace(
                FILE_PREFIX, ""
            )
            if path.exists(private_key_pem) and path.isfile(private_key_pem):
                try:
                    with open(private_key_pem, "r") as privateKeyHandler:
                        resolved_private_key = privateKeyHandler.read()
                except Exception as e:
                    error_msg = f"Could not find Gremlin ALFI PrivateKey at: {raw_private_key_or_file_reference}"
                    logger.critical(error_msg)
                    raise ALFIPrivateKeyException(error_msg) from e
            else:
                error_msg = f"Could not find Gremlin ALFI private key at: {raw_private_key_or_file_reference}"
                logger.critical(error_msg)
                raise ALFIFileNotFoundException(error_msg)
        else:
            resolved_private_key = raw_private_key_or_file_reference
        if GremlinALFICrypto.is_base64_encoded_certificate_or_private_key(
            resolved_private_key
        ):
            return resolved_private_key
        else:
            error_msg = (
                "PrivateKey does not resolve to a valid Base64 encoded string"
            )
            logger.critical(error_msg)
            raise ALFIPrivateKeyException(error_msg)
