# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'GetViewResult',
    'AwaitableGetViewResult',
    'get_view',
    'get_view_output',
]

@pulumi.output_type
class GetViewResult:
    def __init__(__self__, create_time=None, display_name=None, name=None, update_time=None, value=None):
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if display_name and not isinstance(display_name, str):
            raise TypeError("Expected argument 'display_name' to be a str")
        pulumi.set(__self__, "display_name", display_name)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)
        if value and not isinstance(value, str):
            raise TypeError("Expected argument 'value' to be a str")
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The time at which this view was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> str:
        """
        The human-readable display name of the view.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Immutable. The resource name of the view. Format: projects/{project}/locations/{location}/views/{view}
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        The most recent time at which the view was updated.
        """
        return pulumi.get(self, "update_time")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        String with specific view properties.
        """
        return pulumi.get(self, "value")


class AwaitableGetViewResult(GetViewResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetViewResult(
            create_time=self.create_time,
            display_name=self.display_name,
            name=self.name,
            update_time=self.update_time,
            value=self.value)


def get_view(location: Optional[str] = None,
             project: Optional[str] = None,
             view_id: Optional[str] = None,
             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetViewResult:
    """
    Gets a view.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['project'] = project
    __args__['viewId'] = view_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:contactcenterinsights/v1:getView', __args__, opts=opts, typ=GetViewResult).value

    return AwaitableGetViewResult(
        create_time=__ret__.create_time,
        display_name=__ret__.display_name,
        name=__ret__.name,
        update_time=__ret__.update_time,
        value=__ret__.value)


@_utilities.lift_output_func(get_view)
def get_view_output(location: Optional[pulumi.Input[str]] = None,
                    project: Optional[pulumi.Input[Optional[str]]] = None,
                    view_id: Optional[pulumi.Input[str]] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetViewResult]:
    """
    Gets a view.
    """
    ...
