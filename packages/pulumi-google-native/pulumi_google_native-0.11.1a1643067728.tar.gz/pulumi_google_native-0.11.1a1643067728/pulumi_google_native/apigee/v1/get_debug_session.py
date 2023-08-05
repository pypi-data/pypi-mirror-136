# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'GetDebugSessionResult',
    'AwaitableGetDebugSessionResult',
    'get_debug_session',
    'get_debug_session_output',
]

@pulumi.output_type
class GetDebugSessionResult:
    def __init__(__self__, count=None, filter=None, name=None, timeout=None, tracesize=None, validity=None):
        if count and not isinstance(count, int):
            raise TypeError("Expected argument 'count' to be a int")
        pulumi.set(__self__, "count", count)
        if filter and not isinstance(filter, str):
            raise TypeError("Expected argument 'filter' to be a str")
        pulumi.set(__self__, "filter", filter)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if timeout and not isinstance(timeout, str):
            raise TypeError("Expected argument 'timeout' to be a str")
        pulumi.set(__self__, "timeout", timeout)
        if tracesize and not isinstance(tracesize, int):
            raise TypeError("Expected argument 'tracesize' to be a int")
        pulumi.set(__self__, "tracesize", tracesize)
        if validity and not isinstance(validity, int):
            raise TypeError("Expected argument 'validity' to be a int")
        pulumi.set(__self__, "validity", validity)

    @property
    @pulumi.getter
    def count(self) -> int:
        """
        Optional. The number of request to be traced. Min = 1, Max = 15, Default = 10.
        """
        return pulumi.get(self, "count")

    @property
    @pulumi.getter
    def filter(self) -> str:
        """
        Optional. A conditional statement which is evaluated against the request message to determine if it should be traced. Syntax matches that of on API Proxy bundle flow Condition.
        """
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        A unique ID for this DebugSession.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def timeout(self) -> str:
        """
        Optional. The time in seconds after which this DebugSession should end. This value will override the value in query param, if both are provided.
        """
        return pulumi.get(self, "timeout")

    @property
    @pulumi.getter
    def tracesize(self) -> int:
        """
        Optional. The maximum number of bytes captured from the response payload. Min = 0, Max = 5120, Default = 5120.
        """
        return pulumi.get(self, "tracesize")

    @property
    @pulumi.getter
    def validity(self) -> int:
        """
        Optional. The length of time, in seconds, that this debug session is valid, starting from when it's received in the control plane. Min = 1, Max = 15, Default = 10.
        """
        return pulumi.get(self, "validity")


class AwaitableGetDebugSessionResult(GetDebugSessionResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetDebugSessionResult(
            count=self.count,
            filter=self.filter,
            name=self.name,
            timeout=self.timeout,
            tracesize=self.tracesize,
            validity=self.validity)


def get_debug_session(api_id: Optional[str] = None,
                      debugsession_id: Optional[str] = None,
                      environment_id: Optional[str] = None,
                      organization_id: Optional[str] = None,
                      revision_id: Optional[str] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetDebugSessionResult:
    """
    Retrieves a debug session.
    """
    __args__ = dict()
    __args__['apiId'] = api_id
    __args__['debugsessionId'] = debugsession_id
    __args__['environmentId'] = environment_id
    __args__['organizationId'] = organization_id
    __args__['revisionId'] = revision_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:apigee/v1:getDebugSession', __args__, opts=opts, typ=GetDebugSessionResult).value

    return AwaitableGetDebugSessionResult(
        count=__ret__.count,
        filter=__ret__.filter,
        name=__ret__.name,
        timeout=__ret__.timeout,
        tracesize=__ret__.tracesize,
        validity=__ret__.validity)


@_utilities.lift_output_func(get_debug_session)
def get_debug_session_output(api_id: Optional[pulumi.Input[str]] = None,
                             debugsession_id: Optional[pulumi.Input[str]] = None,
                             environment_id: Optional[pulumi.Input[str]] = None,
                             organization_id: Optional[pulumi.Input[str]] = None,
                             revision_id: Optional[pulumi.Input[str]] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetDebugSessionResult]:
    """
    Retrieves a debug session.
    """
    ...
