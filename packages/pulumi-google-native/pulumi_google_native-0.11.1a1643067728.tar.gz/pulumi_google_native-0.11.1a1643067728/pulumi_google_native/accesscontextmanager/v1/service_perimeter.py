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

__all__ = ['ServicePerimeterArgs', 'ServicePerimeter']

@pulumi.input_type
class ServicePerimeterArgs:
    def __init__(__self__, *,
                 access_policy_id: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 perimeter_type: Optional[pulumi.Input['ServicePerimeterPerimeterType']] = None,
                 spec: Optional[pulumi.Input['ServicePerimeterConfigArgs']] = None,
                 status: Optional[pulumi.Input['ServicePerimeterConfigArgs']] = None,
                 title: Optional[pulumi.Input[str]] = None,
                 use_explicit_dry_run_spec: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a ServicePerimeter resource.
        :param pulumi.Input[str] description: Description of the `ServicePerimeter` and its use. Does not affect behavior.
        :param pulumi.Input[str] name: Resource name for the ServicePerimeter. The `short_name` component must begin with a letter and only include alphanumeric and '_'. Format: `accessPolicies/{access_policy}/servicePerimeters/{service_perimeter}`
        :param pulumi.Input['ServicePerimeterPerimeterType'] perimeter_type: Perimeter type indicator. A single project is allowed to be a member of single regular perimeter, but multiple service perimeter bridges. A project cannot be a included in a perimeter bridge without being included in regular perimeter. For perimeter bridges, the restricted service list as well as access level lists must be empty.
        :param pulumi.Input['ServicePerimeterConfigArgs'] spec: Proposed (or dry run) ServicePerimeter configuration. This configuration allows to specify and test ServicePerimeter configuration without enforcing actual access restrictions. Only allowed to be set when the "use_explicit_dry_run_spec" flag is set.
        :param pulumi.Input['ServicePerimeterConfigArgs'] status: Current ServicePerimeter configuration. Specifies sets of resources, restricted services and access levels that determine perimeter content and boundaries.
        :param pulumi.Input[str] title: Human readable title. Must be unique within the Policy.
        :param pulumi.Input[bool] use_explicit_dry_run_spec: Use explicit dry run spec flag. Ordinarily, a dry-run spec implicitly exists for all Service Perimeters, and that spec is identical to the status for those Service Perimeters. When this flag is set, it inhibits the generation of the implicit spec, thereby allowing the user to explicitly provide a configuration ("spec") to use in a dry-run version of the Service Perimeter. This allows the user to test changes to the enforced config ("status") without actually enforcing them. This testing is done through analyzing the differences between currently enforced and suggested restrictions. use_explicit_dry_run_spec must bet set to True if any of the fields in the spec are set to non-default values.
        """
        pulumi.set(__self__, "access_policy_id", access_policy_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if perimeter_type is not None:
            pulumi.set(__self__, "perimeter_type", perimeter_type)
        if spec is not None:
            pulumi.set(__self__, "spec", spec)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if title is not None:
            pulumi.set(__self__, "title", title)
        if use_explicit_dry_run_spec is not None:
            pulumi.set(__self__, "use_explicit_dry_run_spec", use_explicit_dry_run_spec)

    @property
    @pulumi.getter(name="accessPolicyId")
    def access_policy_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "access_policy_id")

    @access_policy_id.setter
    def access_policy_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "access_policy_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of the `ServicePerimeter` and its use. Does not affect behavior.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Resource name for the ServicePerimeter. The `short_name` component must begin with a letter and only include alphanumeric and '_'. Format: `accessPolicies/{access_policy}/servicePerimeters/{service_perimeter}`
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="perimeterType")
    def perimeter_type(self) -> Optional[pulumi.Input['ServicePerimeterPerimeterType']]:
        """
        Perimeter type indicator. A single project is allowed to be a member of single regular perimeter, but multiple service perimeter bridges. A project cannot be a included in a perimeter bridge without being included in regular perimeter. For perimeter bridges, the restricted service list as well as access level lists must be empty.
        """
        return pulumi.get(self, "perimeter_type")

    @perimeter_type.setter
    def perimeter_type(self, value: Optional[pulumi.Input['ServicePerimeterPerimeterType']]):
        pulumi.set(self, "perimeter_type", value)

    @property
    @pulumi.getter
    def spec(self) -> Optional[pulumi.Input['ServicePerimeterConfigArgs']]:
        """
        Proposed (or dry run) ServicePerimeter configuration. This configuration allows to specify and test ServicePerimeter configuration without enforcing actual access restrictions. Only allowed to be set when the "use_explicit_dry_run_spec" flag is set.
        """
        return pulumi.get(self, "spec")

    @spec.setter
    def spec(self, value: Optional[pulumi.Input['ServicePerimeterConfigArgs']]):
        pulumi.set(self, "spec", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input['ServicePerimeterConfigArgs']]:
        """
        Current ServicePerimeter configuration. Specifies sets of resources, restricted services and access levels that determine perimeter content and boundaries.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input['ServicePerimeterConfigArgs']]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def title(self) -> Optional[pulumi.Input[str]]:
        """
        Human readable title. Must be unique within the Policy.
        """
        return pulumi.get(self, "title")

    @title.setter
    def title(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "title", value)

    @property
    @pulumi.getter(name="useExplicitDryRunSpec")
    def use_explicit_dry_run_spec(self) -> Optional[pulumi.Input[bool]]:
        """
        Use explicit dry run spec flag. Ordinarily, a dry-run spec implicitly exists for all Service Perimeters, and that spec is identical to the status for those Service Perimeters. When this flag is set, it inhibits the generation of the implicit spec, thereby allowing the user to explicitly provide a configuration ("spec") to use in a dry-run version of the Service Perimeter. This allows the user to test changes to the enforced config ("status") without actually enforcing them. This testing is done through analyzing the differences between currently enforced and suggested restrictions. use_explicit_dry_run_spec must bet set to True if any of the fields in the spec are set to non-default values.
        """
        return pulumi.get(self, "use_explicit_dry_run_spec")

    @use_explicit_dry_run_spec.setter
    def use_explicit_dry_run_spec(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "use_explicit_dry_run_spec", value)


class ServicePerimeter(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 access_policy_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 perimeter_type: Optional[pulumi.Input['ServicePerimeterPerimeterType']] = None,
                 spec: Optional[pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']]] = None,
                 status: Optional[pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']]] = None,
                 title: Optional[pulumi.Input[str]] = None,
                 use_explicit_dry_run_spec: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        Creates a service perimeter. The long-running operation from this RPC has a successful status after the service perimeter propagates to long-lasting storage. If a service perimeter contains errors, an error response is returned for the first error encountered.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: Description of the `ServicePerimeter` and its use. Does not affect behavior.
        :param pulumi.Input[str] name: Resource name for the ServicePerimeter. The `short_name` component must begin with a letter and only include alphanumeric and '_'. Format: `accessPolicies/{access_policy}/servicePerimeters/{service_perimeter}`
        :param pulumi.Input['ServicePerimeterPerimeterType'] perimeter_type: Perimeter type indicator. A single project is allowed to be a member of single regular perimeter, but multiple service perimeter bridges. A project cannot be a included in a perimeter bridge without being included in regular perimeter. For perimeter bridges, the restricted service list as well as access level lists must be empty.
        :param pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']] spec: Proposed (or dry run) ServicePerimeter configuration. This configuration allows to specify and test ServicePerimeter configuration without enforcing actual access restrictions. Only allowed to be set when the "use_explicit_dry_run_spec" flag is set.
        :param pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']] status: Current ServicePerimeter configuration. Specifies sets of resources, restricted services and access levels that determine perimeter content and boundaries.
        :param pulumi.Input[str] title: Human readable title. Must be unique within the Policy.
        :param pulumi.Input[bool] use_explicit_dry_run_spec: Use explicit dry run spec flag. Ordinarily, a dry-run spec implicitly exists for all Service Perimeters, and that spec is identical to the status for those Service Perimeters. When this flag is set, it inhibits the generation of the implicit spec, thereby allowing the user to explicitly provide a configuration ("spec") to use in a dry-run version of the Service Perimeter. This allows the user to test changes to the enforced config ("status") without actually enforcing them. This testing is done through analyzing the differences between currently enforced and suggested restrictions. use_explicit_dry_run_spec must bet set to True if any of the fields in the spec are set to non-default values.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ServicePerimeterArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a service perimeter. The long-running operation from this RPC has a successful status after the service perimeter propagates to long-lasting storage. If a service perimeter contains errors, an error response is returned for the first error encountered.

        :param str resource_name: The name of the resource.
        :param ServicePerimeterArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ServicePerimeterArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 access_policy_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 perimeter_type: Optional[pulumi.Input['ServicePerimeterPerimeterType']] = None,
                 spec: Optional[pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']]] = None,
                 status: Optional[pulumi.Input[pulumi.InputType['ServicePerimeterConfigArgs']]] = None,
                 title: Optional[pulumi.Input[str]] = None,
                 use_explicit_dry_run_spec: Optional[pulumi.Input[bool]] = None,
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
            __props__ = ServicePerimeterArgs.__new__(ServicePerimeterArgs)

            if access_policy_id is None and not opts.urn:
                raise TypeError("Missing required property 'access_policy_id'")
            __props__.__dict__["access_policy_id"] = access_policy_id
            __props__.__dict__["description"] = description
            __props__.__dict__["name"] = name
            __props__.__dict__["perimeter_type"] = perimeter_type
            __props__.__dict__["spec"] = spec
            __props__.__dict__["status"] = status
            __props__.__dict__["title"] = title
            __props__.__dict__["use_explicit_dry_run_spec"] = use_explicit_dry_run_spec
        super(ServicePerimeter, __self__).__init__(
            'google-native:accesscontextmanager/v1:ServicePerimeter',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'ServicePerimeter':
        """
        Get an existing ServicePerimeter resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ServicePerimeterArgs.__new__(ServicePerimeterArgs)

        __props__.__dict__["description"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["perimeter_type"] = None
        __props__.__dict__["spec"] = None
        __props__.__dict__["status"] = None
        __props__.__dict__["title"] = None
        __props__.__dict__["use_explicit_dry_run_spec"] = None
        return ServicePerimeter(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        Description of the `ServicePerimeter` and its use. Does not affect behavior.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Resource name for the ServicePerimeter. The `short_name` component must begin with a letter and only include alphanumeric and '_'. Format: `accessPolicies/{access_policy}/servicePerimeters/{service_perimeter}`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="perimeterType")
    def perimeter_type(self) -> pulumi.Output[str]:
        """
        Perimeter type indicator. A single project is allowed to be a member of single regular perimeter, but multiple service perimeter bridges. A project cannot be a included in a perimeter bridge without being included in regular perimeter. For perimeter bridges, the restricted service list as well as access level lists must be empty.
        """
        return pulumi.get(self, "perimeter_type")

    @property
    @pulumi.getter
    def spec(self) -> pulumi.Output['outputs.ServicePerimeterConfigResponse']:
        """
        Proposed (or dry run) ServicePerimeter configuration. This configuration allows to specify and test ServicePerimeter configuration without enforcing actual access restrictions. Only allowed to be set when the "use_explicit_dry_run_spec" flag is set.
        """
        return pulumi.get(self, "spec")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output['outputs.ServicePerimeterConfigResponse']:
        """
        Current ServicePerimeter configuration. Specifies sets of resources, restricted services and access levels that determine perimeter content and boundaries.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def title(self) -> pulumi.Output[str]:
        """
        Human readable title. Must be unique within the Policy.
        """
        return pulumi.get(self, "title")

    @property
    @pulumi.getter(name="useExplicitDryRunSpec")
    def use_explicit_dry_run_spec(self) -> pulumi.Output[bool]:
        """
        Use explicit dry run spec flag. Ordinarily, a dry-run spec implicitly exists for all Service Perimeters, and that spec is identical to the status for those Service Perimeters. When this flag is set, it inhibits the generation of the implicit spec, thereby allowing the user to explicitly provide a configuration ("spec") to use in a dry-run version of the Service Perimeter. This allows the user to test changes to the enforced config ("status") without actually enforcing them. This testing is done through analyzing the differences between currently enforced and suggested restrictions. use_explicit_dry_run_spec must bet set to True if any of the fields in the spec are set to non-default values.
        """
        return pulumi.get(self, "use_explicit_dry_run_spec")

