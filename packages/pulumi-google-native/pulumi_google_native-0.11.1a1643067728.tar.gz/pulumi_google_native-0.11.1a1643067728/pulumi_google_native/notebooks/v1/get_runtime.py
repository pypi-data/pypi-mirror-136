# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from . import outputs

__all__ = [
    'GetRuntimeResult',
    'AwaitableGetRuntimeResult',
    'get_runtime',
    'get_runtime_output',
]

@pulumi.output_type
class GetRuntimeResult:
    def __init__(__self__, access_config=None, create_time=None, health_state=None, metrics=None, name=None, software_config=None, state=None, update_time=None, virtual_machine=None):
        if access_config and not isinstance(access_config, dict):
            raise TypeError("Expected argument 'access_config' to be a dict")
        pulumi.set(__self__, "access_config", access_config)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if health_state and not isinstance(health_state, str):
            raise TypeError("Expected argument 'health_state' to be a str")
        pulumi.set(__self__, "health_state", health_state)
        if metrics and not isinstance(metrics, dict):
            raise TypeError("Expected argument 'metrics' to be a dict")
        pulumi.set(__self__, "metrics", metrics)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if software_config and not isinstance(software_config, dict):
            raise TypeError("Expected argument 'software_config' to be a dict")
        pulumi.set(__self__, "software_config", software_config)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)
        if virtual_machine and not isinstance(virtual_machine, dict):
            raise TypeError("Expected argument 'virtual_machine' to be a dict")
        pulumi.set(__self__, "virtual_machine", virtual_machine)

    @property
    @pulumi.getter(name="accessConfig")
    def access_config(self) -> 'outputs.RuntimeAccessConfigResponse':
        """
        The config settings for accessing runtime.
        """
        return pulumi.get(self, "access_config")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        Runtime creation time.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="healthState")
    def health_state(self) -> str:
        """
        Runtime health_state.
        """
        return pulumi.get(self, "health_state")

    @property
    @pulumi.getter
    def metrics(self) -> 'outputs.RuntimeMetricsResponse':
        """
        Contains Runtime daemon metrics such as Service status and JupyterLab stats.
        """
        return pulumi.get(self, "metrics")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The resource name of the runtime. Format: `projects/{project}/locations/{location}/runtimes/{runtimeId}`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="softwareConfig")
    def software_config(self) -> 'outputs.RuntimeSoftwareConfigResponse':
        """
        The config settings for software inside the runtime.
        """
        return pulumi.get(self, "software_config")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        Runtime state.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        Runtime update time.
        """
        return pulumi.get(self, "update_time")

    @property
    @pulumi.getter(name="virtualMachine")
    def virtual_machine(self) -> 'outputs.VirtualMachineResponse':
        """
        Use a Compute Engine VM image to start the managed notebook instance.
        """
        return pulumi.get(self, "virtual_machine")


class AwaitableGetRuntimeResult(GetRuntimeResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRuntimeResult(
            access_config=self.access_config,
            create_time=self.create_time,
            health_state=self.health_state,
            metrics=self.metrics,
            name=self.name,
            software_config=self.software_config,
            state=self.state,
            update_time=self.update_time,
            virtual_machine=self.virtual_machine)


def get_runtime(location: Optional[str] = None,
                project: Optional[str] = None,
                runtime_id: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRuntimeResult:
    """
    Gets details of a single Runtime. The location must be a regional endpoint rather than zonal.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['project'] = project
    __args__['runtimeId'] = runtime_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:notebooks/v1:getRuntime', __args__, opts=opts, typ=GetRuntimeResult).value

    return AwaitableGetRuntimeResult(
        access_config=__ret__.access_config,
        create_time=__ret__.create_time,
        health_state=__ret__.health_state,
        metrics=__ret__.metrics,
        name=__ret__.name,
        software_config=__ret__.software_config,
        state=__ret__.state,
        update_time=__ret__.update_time,
        virtual_machine=__ret__.virtual_machine)


@_utilities.lift_output_func(get_runtime)
def get_runtime_output(location: Optional[pulumi.Input[str]] = None,
                       project: Optional[pulumi.Input[Optional[str]]] = None,
                       runtime_id: Optional[pulumi.Input[str]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRuntimeResult]:
    """
    Gets details of a single Runtime. The location must be a regional endpoint rather than zonal.
    """
    ...
