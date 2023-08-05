# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from . import outputs
from ._inputs import *

__all__ = ['AnnotationSpecSetArgs', 'AnnotationSpecSet']

@pulumi.input_type
class AnnotationSpecSetArgs:
    def __init__(__self__, *,
                 annotation_specs: pulumi.Input[Sequence[pulumi.Input['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]],
                 display_name: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a AnnotationSpecSet resource.
        :param pulumi.Input[Sequence[pulumi.Input['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]] annotation_specs: The array of AnnotationSpecs that you define when you create the AnnotationSpecSet. These are the possible labels for the labeling task.
        :param pulumi.Input[str] display_name: The display name for AnnotationSpecSet that you define when you create it. Maximum of 64 characters.
        :param pulumi.Input[str] description: Optional. User-provided description of the annotation specification set. The description can be up to 10,000 characters long.
        """
        pulumi.set(__self__, "annotation_specs", annotation_specs)
        pulumi.set(__self__, "display_name", display_name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter(name="annotationSpecs")
    def annotation_specs(self) -> pulumi.Input[Sequence[pulumi.Input['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]]:
        """
        The array of AnnotationSpecs that you define when you create the AnnotationSpecSet. These are the possible labels for the labeling task.
        """
        return pulumi.get(self, "annotation_specs")

    @annotation_specs.setter
    def annotation_specs(self, value: pulumi.Input[Sequence[pulumi.Input['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]]):
        pulumi.set(self, "annotation_specs", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Input[str]:
        """
        The display name for AnnotationSpecSet that you define when you create it. Maximum of 64 characters.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. User-provided description of the annotation specification set. The description can be up to 10,000 characters long.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)


class AnnotationSpecSet(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotation_specs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates an annotation spec set by providing a set of labels.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]]] annotation_specs: The array of AnnotationSpecs that you define when you create the AnnotationSpecSet. These are the possible labels for the labeling task.
        :param pulumi.Input[str] description: Optional. User-provided description of the annotation specification set. The description can be up to 10,000 characters long.
        :param pulumi.Input[str] display_name: The display name for AnnotationSpecSet that you define when you create it. Maximum of 64 characters.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: AnnotationSpecSetArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates an annotation spec set by providing a set of labels.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param AnnotationSpecSetArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AnnotationSpecSetArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotation_specs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1AnnotationSpecArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
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
            __props__ = AnnotationSpecSetArgs.__new__(AnnotationSpecSetArgs)

            if annotation_specs is None and not opts.urn:
                raise TypeError("Missing required property 'annotation_specs'")
            __props__.__dict__["annotation_specs"] = annotation_specs
            __props__.__dict__["description"] = description
            if display_name is None and not opts.urn:
                raise TypeError("Missing required property 'display_name'")
            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["project"] = project
            __props__.__dict__["blocking_resources"] = None
            __props__.__dict__["name"] = None
        super(AnnotationSpecSet, __self__).__init__(
            'google-native:datalabeling/v1beta1:AnnotationSpecSet',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'AnnotationSpecSet':
        """
        Get an existing AnnotationSpecSet resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = AnnotationSpecSetArgs.__new__(AnnotationSpecSetArgs)

        __props__.__dict__["annotation_specs"] = None
        __props__.__dict__["blocking_resources"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["name"] = None
        return AnnotationSpecSet(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="annotationSpecs")
    def annotation_specs(self) -> pulumi.Output[Sequence['outputs.GoogleCloudDatalabelingV1beta1AnnotationSpecResponse']]:
        """
        The array of AnnotationSpecs that you define when you create the AnnotationSpecSet. These are the possible labels for the labeling task.
        """
        return pulumi.get(self, "annotation_specs")

    @property
    @pulumi.getter(name="blockingResources")
    def blocking_resources(self) -> pulumi.Output[Sequence[str]]:
        """
        The names of any related resources that are blocking changes to the annotation spec set.
        """
        return pulumi.get(self, "blocking_resources")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        Optional. User-provided description of the annotation specification set. The description can be up to 10,000 characters long.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        The display name for AnnotationSpecSet that you define when you create it. Maximum of 64 characters.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The AnnotationSpecSet resource name in the following format: "projects/{project_id}/annotationSpecSets/{annotation_spec_set_id}"
        """
        return pulumi.get(self, "name")

