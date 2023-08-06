# -*- coding: utf-8 -*-
#
# Copyright (C) Gremlin Inc <sales@gremlin.com> - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

class BaseALFIException(Exception):
    """Base ALFI Exception class"""


class ALFIConfigurationException(BaseALFIException):
    """Exception for improper or missing configuration"""

    def __init__(self, message):
        super(ALFIConfigurationException, self).__init__(message)


class ALFIFileNotFoundException(BaseALFIException):
    """Exception for missing or bad file"""

    def __init__(self, message):
        super(ALFIFileNotFoundException, self).__init__(message)


class ALFICertificateException(BaseALFIException):
    """Exception for bad certificate"""

    def __init__(self, message):
        super(ALFICertificateException, self).__init__(message)


class ALFIAttackImpact(BaseALFIException):
    """Exception for Impacting a function"""

    def __init__(self, message):
        super(ALFIAttackImpact, self).__init__(message)


class ALFIPrivateKeyException(BaseALFIException):
    """Exception for bad private key"""

    def __init__(self, message):
        super(ALFIPrivateKeyException, self).__init__(message)


class ALFIIllegalArgumentException(BaseALFIException):
    """Exception for bad argument"""

    def __init__(self, message):
        super(ALFIIllegalArgumentException, self).__init__(message)


class ALFIIllegalStateException(BaseALFIException):
    """Exception for bad state"""

    def __init__(self, message):
        super(ALFIIllegalStateException, self).__init__(message)


class ALFIRuntimeException(BaseALFIException):
    """Exception for runtime errors"""

    def __init__(self, message):
        super(ALFIRuntimeException, self).__init__(message)


class ALFIIntentionalException(BaseALFIException):
    """Exception for Intentional Experiment Exceptions"""

    def __init__(self, message):
        super(ALFIIntentionalException, self).__init__(message)


class ALFIApiClientException(BaseALFIException):
    """Exception for Alfi API Client import errors"""

    def __init__(self, message):
        super(ALFIApiClientException, self).__init__(message)
