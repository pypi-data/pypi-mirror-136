# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'CaseSeverity',
]


class CaseSeverity(str, Enum):
    """
    The severity of this case.
    """
    SEVERITY_UNSPECIFIED = "SEVERITY_UNSPECIFIED"
    """
    Severity is undefined or has not been set yet.
    """
    S0 = "S0"
    """
    Extreme impact on a production service. Service is hard down.
    """
    S1 = "S1"
    """
    Critical impact on a production service. Service is currently unusable.
    """
    S2 = "S2"
    """
    Severe impact on a production service. Service is usable but greatly impaired.
    """
    S3 = "S3"
    """
    Medium impact on a production service. Service is available, but moderately impaired.
    """
    S4 = "S4"
    """
    General questions or minor issues. Production service is fully available.
    """
