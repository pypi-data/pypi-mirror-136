# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'AuditLogConfigLogType',
    'FunctionIngressSettings',
    'FunctionVpcConnectorEgressSettings',
    'HttpsTriggerSecurityLevel',
]


class AuditLogConfigLogType(str, Enum):
    """
    The log type that this config enables.
    """
    LOG_TYPE_UNSPECIFIED = "LOG_TYPE_UNSPECIFIED"
    """
    Default case. Should never be this.
    """
    ADMIN_READ = "ADMIN_READ"
    """
    Admin reads. Example: CloudIAM getIamPolicy
    """
    DATA_WRITE = "DATA_WRITE"
    """
    Data writes. Example: CloudSQL Users create
    """
    DATA_READ = "DATA_READ"
    """
    Data reads. Example: CloudSQL Users list
    """


class FunctionIngressSettings(str, Enum):
    """
    The ingress settings for the function, controlling what traffic can reach it.
    """
    INGRESS_SETTINGS_UNSPECIFIED = "INGRESS_SETTINGS_UNSPECIFIED"
    """
    Unspecified.
    """
    ALLOW_ALL = "ALLOW_ALL"
    """
    Allow HTTP traffic from public and private sources.
    """
    ALLOW_INTERNAL_ONLY = "ALLOW_INTERNAL_ONLY"
    """
    Allow HTTP traffic from only private VPC sources.
    """
    ALLOW_INTERNAL_AND_GCLB = "ALLOW_INTERNAL_AND_GCLB"
    """
    Allow HTTP traffic from private VPC sources and through GCLB.
    """


class FunctionVpcConnectorEgressSettings(str, Enum):
    """
    The egress settings for the connector, controlling what traffic is diverted through it.
    """
    VPC_CONNECTOR_EGRESS_SETTINGS_UNSPECIFIED = "VPC_CONNECTOR_EGRESS_SETTINGS_UNSPECIFIED"
    """
    Unspecified.
    """
    PRIVATE_RANGES_ONLY = "PRIVATE_RANGES_ONLY"
    """
    Use the VPC Access Connector only for private IP space from RFC1918.
    """
    ALL_TRAFFIC = "ALL_TRAFFIC"
    """
    Force the use of VPC Access Connector for all egress traffic from the function.
    """


class HttpsTriggerSecurityLevel(str, Enum):
    """
    The security level for the function.
    """
    SECURITY_LEVEL_UNSPECIFIED = "SECURITY_LEVEL_UNSPECIFIED"
    """
    Unspecified.
    """
    SECURE_ALWAYS = "SECURE_ALWAYS"
    """
    Requests for a URL that match this handler that do not use HTTPS are automatically redirected to the HTTPS URL with the same path. Query parameters are reserved for the redirect.
    """
    SECURE_OPTIONAL = "SECURE_OPTIONAL"
    """
    Both HTTP and HTTPS requests with URLs that match the handler succeed without redirects. The application can examine the request to determine which protocol was used and respond accordingly.
    """
