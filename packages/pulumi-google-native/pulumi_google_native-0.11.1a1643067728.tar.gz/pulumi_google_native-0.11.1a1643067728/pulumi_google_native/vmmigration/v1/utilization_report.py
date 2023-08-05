# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from . import outputs
from ._enums import *
from ._inputs import *

__all__ = ['UtilizationReportArgs', 'UtilizationReport']

@pulumi.input_type
class UtilizationReportArgs:
    def __init__(__self__, *,
                 source_id: pulumi.Input[str],
                 utilization_report_id: pulumi.Input[str],
                 display_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 time_frame: Optional[pulumi.Input['UtilizationReportTimeFrame']] = None,
                 vms: Optional[pulumi.Input[Sequence[pulumi.Input['VmUtilizationInfoArgs']]]] = None):
        """
        The set of arguments for constructing a UtilizationReport resource.
        :param pulumi.Input[str] display_name: The report display name, as assigned by the user.
        :param pulumi.Input['UtilizationReportTimeFrame'] time_frame: Time frame of the report.
        :param pulumi.Input[Sequence[pulumi.Input['VmUtilizationInfoArgs']]] vms: List of utilization information per VM. When sent as part of the request, the "vm_id" field is used in order to specify which VMs to include in the report. In that case all other fields are ignored.
        """
        pulumi.set(__self__, "source_id", source_id)
        pulumi.set(__self__, "utilization_report_id", utilization_report_id)
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if request_id is not None:
            pulumi.set(__self__, "request_id", request_id)
        if time_frame is not None:
            pulumi.set(__self__, "time_frame", time_frame)
        if vms is not None:
            pulumi.set(__self__, "vms", vms)

    @property
    @pulumi.getter(name="sourceId")
    def source_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "source_id")

    @source_id.setter
    def source_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "source_id", value)

    @property
    @pulumi.getter(name="utilizationReportId")
    def utilization_report_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "utilization_report_id")

    @utilization_report_id.setter
    def utilization_report_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "utilization_report_id", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        The report display name, as assigned by the user.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "request_id")

    @request_id.setter
    def request_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "request_id", value)

    @property
    @pulumi.getter(name="timeFrame")
    def time_frame(self) -> Optional[pulumi.Input['UtilizationReportTimeFrame']]:
        """
        Time frame of the report.
        """
        return pulumi.get(self, "time_frame")

    @time_frame.setter
    def time_frame(self, value: Optional[pulumi.Input['UtilizationReportTimeFrame']]):
        pulumi.set(self, "time_frame", value)

    @property
    @pulumi.getter
    def vms(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['VmUtilizationInfoArgs']]]]:
        """
        List of utilization information per VM. When sent as part of the request, the "vm_id" field is used in order to specify which VMs to include in the report. In that case all other fields are ignored.
        """
        return pulumi.get(self, "vms")

    @vms.setter
    def vms(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['VmUtilizationInfoArgs']]]]):
        pulumi.set(self, "vms", value)


class UtilizationReport(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 source_id: Optional[pulumi.Input[str]] = None,
                 time_frame: Optional[pulumi.Input['UtilizationReportTimeFrame']] = None,
                 utilization_report_id: Optional[pulumi.Input[str]] = None,
                 vms: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['VmUtilizationInfoArgs']]]]] = None,
                 __props__=None):
        """
        Creates a new UtilizationReport.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: The report display name, as assigned by the user.
        :param pulumi.Input['UtilizationReportTimeFrame'] time_frame: Time frame of the report.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['VmUtilizationInfoArgs']]]] vms: List of utilization information per VM. When sent as part of the request, the "vm_id" field is used in order to specify which VMs to include in the report. In that case all other fields are ignored.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: UtilizationReportArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new UtilizationReport.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param UtilizationReportArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(UtilizationReportArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 source_id: Optional[pulumi.Input[str]] = None,
                 time_frame: Optional[pulumi.Input['UtilizationReportTimeFrame']] = None,
                 utilization_report_id: Optional[pulumi.Input[str]] = None,
                 vms: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['VmUtilizationInfoArgs']]]]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = UtilizationReportArgs.__new__(UtilizationReportArgs)

            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["location"] = location
            __props__.__dict__["project"] = project
            __props__.__dict__["request_id"] = request_id
            if source_id is None and not opts.urn:
                raise TypeError("Missing required property 'source_id'")
            __props__.__dict__["source_id"] = source_id
            __props__.__dict__["time_frame"] = time_frame
            if utilization_report_id is None and not opts.urn:
                raise TypeError("Missing required property 'utilization_report_id'")
            __props__.__dict__["utilization_report_id"] = utilization_report_id
            __props__.__dict__["vms"] = vms
            __props__.__dict__["create_time"] = None
            __props__.__dict__["error"] = None
            __props__.__dict__["frame_end_time"] = None
            __props__.__dict__["name"] = None
            __props__.__dict__["state"] = None
            __props__.__dict__["state_time"] = None
            __props__.__dict__["vm_count"] = None
        super(UtilizationReport, __self__).__init__(
            'google-native:vmmigration/v1:UtilizationReport',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'UtilizationReport':
        """
        Get an existing UtilizationReport resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = UtilizationReportArgs.__new__(UtilizationReportArgs)

        __props__.__dict__["create_time"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["error"] = None
        __props__.__dict__["frame_end_time"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["state_time"] = None
        __props__.__dict__["time_frame"] = None
        __props__.__dict__["vm_count"] = None
        __props__.__dict__["vms"] = None
        return UtilizationReport(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        The time the report was created (this refers to the time of the request, not the time the report creation completed).
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        The report display name, as assigned by the user.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def error(self) -> pulumi.Output['outputs.StatusResponse']:
        """
        Provides details on the state of the report in case of an error.
        """
        return pulumi.get(self, "error")

    @property
    @pulumi.getter(name="frameEndTime")
    def frame_end_time(self) -> pulumi.Output[str]:
        """
        The point in time when the time frame ends. Notice that the time frame is counted backwards. For instance if the "frame_end_time" value is 2021/01/20 and the time frame is WEEK then the report covers the week between 2021/01/20 and 2021/01/14.
        """
        return pulumi.get(self, "frame_end_time")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The report unique name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        Current state of the report.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="stateTime")
    def state_time(self) -> pulumi.Output[str]:
        """
        The time the state was last set.
        """
        return pulumi.get(self, "state_time")

    @property
    @pulumi.getter(name="timeFrame")
    def time_frame(self) -> pulumi.Output[str]:
        """
        Time frame of the report.
        """
        return pulumi.get(self, "time_frame")

    @property
    @pulumi.getter(name="vmCount")
    def vm_count(self) -> pulumi.Output[int]:
        """
        Total number of VMs included in the report.
        """
        return pulumi.get(self, "vm_count")

    @property
    @pulumi.getter
    def vms(self) -> pulumi.Output[Sequence['outputs.VmUtilizationInfoResponse']]:
        """
        List of utilization information per VM. When sent as part of the request, the "vm_id" field is used in order to specify which VMs to include in the report. In that case all other fields are ignored.
        """
        return pulumi.get(self, "vms")

