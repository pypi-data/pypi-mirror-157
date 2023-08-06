# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from __future__ import annotations

import base64
import logging

from .AlfiConstants import (
    logger_name,
    CERTIFICATE_PREAMBLE,
    CERTIFICATE_POSTAMBLE,
    PRIVATE_KEY_PREAMBLE,
    PRIVATE_KEY_POSTAMBLE,
)
from .Exceptions import ALFIConfigurationException

from asn1crypto.algos import (
    DigestAlgorithm,
    SignedDigestAlgorithm,
    SignedDigestAlgorithmId,
    DigestAlgorithmId,
    DigestInfo,
)
from asn1crypto.cms import (
    ContentInfo,
    ContentType,
    IssuerAndSerialNumber,
    CMSAttribute,
    CMSAttributes,
    GeneralizedTime,
    OctetString,
    UTCTime,
    CMSVersion,
    SignerInfo,
    SignerInfos,
    DigestAlgorithms,
    SignedData,
    SignerIdentifier,
)
from asn1crypto.pem import unarmor
from asn1crypto.x509 import Certificate

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

from datetime import datetime, timezone

from functools import lru_cache

from typing import ClassVar

logger = logging.getLogger(f"{logger_name}.{__name__}")


class GremlinALFICrypto:
    """
    Validate the public/private keypair are usable

    For each request from :ref:`GremlinApiClient` to the Gremlin control plane:
      - Cryptographically generate an asymmetric key for the header authentication from the private key
      - Sign the request payload with the public key for validation with a control-plane copy of the private key
    """

    # Signing mode can be 'fips-186-3 or deterministic-rfc6979
    # see https://www.pycryptodome.org/en/latest/src/signature/dsa.html
    # Gremlin is using `fips-186-3`
    MODE: ClassVar[str] = "fips-186-3"
    ENCODING: ClassVar[str] = "utf-8"

    @classmethod
    @lru_cache(maxsize=2)
    def is_base64_encoded_certificate_or_private_key(cls, s: str) -> bool:
        if logger.getEffectiveLevel() is logging.DEBUG:
            logger.debug(f"Validating if {s} is a valid certificate")
        for r in [
            CERTIFICATE_PREAMBLE,
            CERTIFICATE_POSTAMBLE,
            PRIVATE_KEY_PREAMBLE,
            PRIVATE_KEY_POSTAMBLE,
            "\n",
        ]:
            s = s.replace(r, "")
        try:
            return (
                base64.b64encode(base64.b64decode(s)).decode(cls.ENCODING) == s
            )
        except Exception:
            return False

    @staticmethod
    @lru_cache(maxsize=2)
    def _load_private_key(certificate: str, privateKey: str) -> object:
        cert = ECC.import_key(certificate)
        key = ECC.import_key(privateKey)
        if not (
            cert.pointQ.x == key.pointQ.x and cert.pointQ.y == key.pointQ.y
        ):
            error_msg = (
                "Public and Private key certificates are not a matched set, "
                + "encryption cannot be facilitated."
            )
            logger.critical(error_msg)
            raise ALFIConfigurationException(error_msg)
        return key

    @classmethod
    def build_signature(
        cls, team_id: str, certificate: str, private_key: str
    ) -> str:
        """

        :param team_id:
        :param certificate:
        :param private_key:
        :return:
        """
        if not team_id:
            error_msg = "build_signature requires a teamId, received none"
            logger.critical(error_msg)
            raise ALFIConfigurationException(error_msg)
        signature = cls.sign_timestamp(
            datetime.utcnow().isoformat(), certificate, private_key
        )
        signature_tuple = f"{team_id}:{str(signature, cls.ENCODING)}"
        return str(
            base64.b64encode(bytes(signature_tuple, cls.ENCODING)),
            cls.ENCODING,
        )

    @classmethod
    @lru_cache(maxsize=1)
    def sign_timestamp(
        cls,
        timestamp: str = datetime.utcnow().isoformat(),
        certificate: str = None,
        private_key: str = None,
    ) -> bytes:
        return cls.sign(
            bytes(timestamp, cls.ENCODING), certificate, private_key
        )

    @classmethod
    @lru_cache(maxsize=1)
    def sign(cls, content: bytes, certificate: str, private_key: str) -> bytes:
        """
        Create a CMS enveloped signature

        :param content:
        :param certificate:
        :param private_key:
        :return:
        """
        if cls.is_base64_encoded_certificate_or_private_key(private_key):
            key = cls._load_private_key(certificate, private_key)

        if cls.is_base64_encoded_certificate_or_private_key(certificate):
            cert = Certificate.load(
                unarmor(bytes(certificate, cls.ENCODING))[2]
            )

        ci = ContentInfo(
            {
                "content_type": ContentType("data"),
                "content": content,
            }
        )

        ias = IssuerAndSerialNumber(
            {"issuer": cert.issuer, "serial_number": cert.serial_number}
        )

        # 3 Attributes that need to be signed
        content_attr = CMSAttribute(
            {"type": "content_type", "values": [ContentType("data")]}
        )

        signing_time_attr = CMSAttribute(
            {
                "type": "signing_time",
                "values": [UTCTime(datetime.now(timezone.utc))],
            }
        )

        content_digest = SHA256.new(content).digest()
        digest_attr = CMSAttribute(
            {
                "type": "message_digest",
                "values": [OctetString(content_digest)],
            }
        )

        cms_attributes = CMSAttributes(
            [content_attr, signing_time_attr, digest_attr]
        )

        signer = DSS.new(key, cls.MODE, encoding="der")
        encoded_content = SHA256.new(cms_attributes.dump())
        signed_attributes_digest = signer.sign(encoded_content)

        digest_algorithm = DigestAlgorithm(
            {"algorithm": DigestAlgorithmId("sha256")}
        )

        signer_info = SignerInfo(
            {
                "version": CMSVersion(1),
                "sid": SignerIdentifier("issuer_and_serial_number", ias),
                "digest_algorithm": digest_algorithm,
                "signed_attrs": cms_attributes,
                "signature_algorithm": SignedDigestAlgorithm(
                    {"algorithm": SignedDigestAlgorithmId("sha256_ecdsa")}
                ),
                "signature": OctetString(signed_attributes_digest),
            }
        )

        signed_data = SignedData(
            {
                "version": CMSVersion(1),
                "certificates": [cert],
                "signer_infos": [signer_info],
                "digest_algorithms": DigestAlgorithms([digest_algorithm]),
                "encap_content_info": ci,
            }
        )

        signed_data_content_info = ContentInfo(
            {
                "content_type": ContentType("signed_data"),
                "content": signed_data,
            }
        )

        return base64.b64encode(signed_data_content_info.dump())
