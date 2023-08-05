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

__all__ = ['ConnectionArgs', 'Connection']

@pulumi.input_type
class ConnectionArgs:
    def __init__(__self__, *,
                 connection_id: pulumi.Input[str],
                 connector_version: pulumi.Input[str],
                 auth_config: Optional[pulumi.Input['AuthConfigArgs']] = None,
                 config_variables: Optional[pulumi.Input[Sequence[pulumi.Input['ConfigVariableArgs']]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 inactive: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 lock_config: Optional[pulumi.Input['LockConfigArgs']] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_account: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Connection resource.
        :param pulumi.Input[str] connector_version: Connector version on which the connection is created. The format is: projects/*/locations/global/providers/*/connectors/*/versions/*
        :param pulumi.Input['AuthConfigArgs'] auth_config: Optional. Configuration for establishing the connection's authentication with an external system.
        :param pulumi.Input[Sequence[pulumi.Input['ConfigVariableArgs']]] config_variables: Optional. Configuration for configuring the connection with an external system.
        :param pulumi.Input[str] description: Optional. Description of the resource.
        :param pulumi.Input[bool] inactive: Optional. Inactive indicates the connection is active to use or not.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Optional. Resource labels to represent user-provided metadata. Refer to cloud documentation on labels for more details. https://cloud.google.com/compute/docs/labeling-resources
        :param pulumi.Input['LockConfigArgs'] lock_config: Optional. Configuration that indicates whether or not the Connection can be edited.
        :param pulumi.Input[str] service_account: Optional. Service account needed for runtime plane to access GCP resources.
        """
        pulumi.set(__self__, "connection_id", connection_id)
        pulumi.set(__self__, "connector_version", connector_version)
        if auth_config is not None:
            pulumi.set(__self__, "auth_config", auth_config)
        if config_variables is not None:
            pulumi.set(__self__, "config_variables", config_variables)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if inactive is not None:
            pulumi.set(__self__, "inactive", inactive)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if lock_config is not None:
            pulumi.set(__self__, "lock_config", lock_config)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if service_account is not None:
            pulumi.set(__self__, "service_account", service_account)

    @property
    @pulumi.getter(name="connectionId")
    def connection_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "connection_id")

    @connection_id.setter
    def connection_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "connection_id", value)

    @property
    @pulumi.getter(name="connectorVersion")
    def connector_version(self) -> pulumi.Input[str]:
        """
        Connector version on which the connection is created. The format is: projects/*/locations/global/providers/*/connectors/*/versions/*
        """
        return pulumi.get(self, "connector_version")

    @connector_version.setter
    def connector_version(self, value: pulumi.Input[str]):
        pulumi.set(self, "connector_version", value)

    @property
    @pulumi.getter(name="authConfig")
    def auth_config(self) -> Optional[pulumi.Input['AuthConfigArgs']]:
        """
        Optional. Configuration for establishing the connection's authentication with an external system.
        """
        return pulumi.get(self, "auth_config")

    @auth_config.setter
    def auth_config(self, value: Optional[pulumi.Input['AuthConfigArgs']]):
        pulumi.set(self, "auth_config", value)

    @property
    @pulumi.getter(name="configVariables")
    def config_variables(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ConfigVariableArgs']]]]:
        """
        Optional. Configuration for configuring the connection with an external system.
        """
        return pulumi.get(self, "config_variables")

    @config_variables.setter
    def config_variables(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ConfigVariableArgs']]]]):
        pulumi.set(self, "config_variables", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Description of the resource.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def inactive(self) -> Optional[pulumi.Input[bool]]:
        """
        Optional. Inactive indicates the connection is active to use or not.
        """
        return pulumi.get(self, "inactive")

    @inactive.setter
    def inactive(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "inactive", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Optional. Resource labels to represent user-provided metadata. Refer to cloud documentation on labels for more details. https://cloud.google.com/compute/docs/labeling-resources
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="lockConfig")
    def lock_config(self) -> Optional[pulumi.Input['LockConfigArgs']]:
        """
        Optional. Configuration that indicates whether or not the Connection can be edited.
        """
        return pulumi.get(self, "lock_config")

    @lock_config.setter
    def lock_config(self, value: Optional[pulumi.Input['LockConfigArgs']]):
        pulumi.set(self, "lock_config", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Service account needed for runtime plane to access GCP resources.
        """
        return pulumi.get(self, "service_account")

    @service_account.setter
    def service_account(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_account", value)


class Connection(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auth_config: Optional[pulumi.Input[pulumi.InputType['AuthConfigArgs']]] = None,
                 config_variables: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ConfigVariableArgs']]]]] = None,
                 connection_id: Optional[pulumi.Input[str]] = None,
                 connector_version: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 inactive: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 lock_config: Optional[pulumi.Input[pulumi.InputType['LockConfigArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_account: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a new Connection in a given project and location.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['AuthConfigArgs']] auth_config: Optional. Configuration for establishing the connection's authentication with an external system.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ConfigVariableArgs']]]] config_variables: Optional. Configuration for configuring the connection with an external system.
        :param pulumi.Input[str] connector_version: Connector version on which the connection is created. The format is: projects/*/locations/global/providers/*/connectors/*/versions/*
        :param pulumi.Input[str] description: Optional. Description of the resource.
        :param pulumi.Input[bool] inactive: Optional. Inactive indicates the connection is active to use or not.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Optional. Resource labels to represent user-provided metadata. Refer to cloud documentation on labels for more details. https://cloud.google.com/compute/docs/labeling-resources
        :param pulumi.Input[pulumi.InputType['LockConfigArgs']] lock_config: Optional. Configuration that indicates whether or not the Connection can be edited.
        :param pulumi.Input[str] service_account: Optional. Service account needed for runtime plane to access GCP resources.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ConnectionArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new Connection in a given project and location.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param ConnectionArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConnectionArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auth_config: Optional[pulumi.Input[pulumi.InputType['AuthConfigArgs']]] = None,
                 config_variables: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ConfigVariableArgs']]]]] = None,
                 connection_id: Optional[pulumi.Input[str]] = None,
                 connector_version: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 inactive: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 lock_config: Optional[pulumi.Input[pulumi.InputType['LockConfigArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_account: Optional[pulumi.Input[str]] = None,
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
            __props__ = ConnectionArgs.__new__(ConnectionArgs)

            __props__.__dict__["auth_config"] = auth_config
            __props__.__dict__["config_variables"] = config_variables
            if connection_id is None and not opts.urn:
                raise TypeError("Missing required property 'connection_id'")
            __props__.__dict__["connection_id"] = connection_id
            if connector_version is None and not opts.urn:
                raise TypeError("Missing required property 'connector_version'")
            __props__.__dict__["connector_version"] = connector_version
            __props__.__dict__["description"] = description
            __props__.__dict__["inactive"] = inactive
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["lock_config"] = lock_config
            __props__.__dict__["project"] = project
            __props__.__dict__["service_account"] = service_account
            __props__.__dict__["create_time"] = None
            __props__.__dict__["egress_backends"] = None
            __props__.__dict__["envoy_image_location"] = None
            __props__.__dict__["image_location"] = None
            __props__.__dict__["name"] = None
            __props__.__dict__["service_directory"] = None
            __props__.__dict__["status"] = None
            __props__.__dict__["update_time"] = None
        super(Connection, __self__).__init__(
            'google-native:connectors/v1:Connection',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Connection':
        """
        Get an existing Connection resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ConnectionArgs.__new__(ConnectionArgs)

        __props__.__dict__["auth_config"] = None
        __props__.__dict__["config_variables"] = None
        __props__.__dict__["connector_version"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["egress_backends"] = None
        __props__.__dict__["envoy_image_location"] = None
        __props__.__dict__["image_location"] = None
        __props__.__dict__["inactive"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["lock_config"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["service_account"] = None
        __props__.__dict__["service_directory"] = None
        __props__.__dict__["status"] = None
        __props__.__dict__["update_time"] = None
        return Connection(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="authConfig")
    def auth_config(self) -> pulumi.Output['outputs.AuthConfigResponse']:
        """
        Optional. Configuration for establishing the connection's authentication with an external system.
        """
        return pulumi.get(self, "auth_config")

    @property
    @pulumi.getter(name="configVariables")
    def config_variables(self) -> pulumi.Output[Sequence['outputs.ConfigVariableResponse']]:
        """
        Optional. Configuration for configuring the connection with an external system.
        """
        return pulumi.get(self, "config_variables")

    @property
    @pulumi.getter(name="connectorVersion")
    def connector_version(self) -> pulumi.Output[str]:
        """
        Connector version on which the connection is created. The format is: projects/*/locations/global/providers/*/connectors/*/versions/*
        """
        return pulumi.get(self, "connector_version")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        Created time.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        Optional. Description of the resource.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="egressBackends")
    def egress_backends(self) -> pulumi.Output[Sequence[str]]:
        """
        Outbound domains/hosts needs to be allowlisted.
        """
        return pulumi.get(self, "egress_backends")

    @property
    @pulumi.getter(name="envoyImageLocation")
    def envoy_image_location(self) -> pulumi.Output[str]:
        """
        GCR location where the envoy image is stored. formatted like: gcr.io/{bucketName}/{imageName}
        """
        return pulumi.get(self, "envoy_image_location")

    @property
    @pulumi.getter(name="imageLocation")
    def image_location(self) -> pulumi.Output[str]:
        """
        GCR location where the runtime image is stored. formatted like: gcr.io/{bucketName}/{imageName}
        """
        return pulumi.get(self, "image_location")

    @property
    @pulumi.getter
    def inactive(self) -> pulumi.Output[bool]:
        """
        Optional. Inactive indicates the connection is active to use or not.
        """
        return pulumi.get(self, "inactive")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Optional. Resource labels to represent user-provided metadata. Refer to cloud documentation on labels for more details. https://cloud.google.com/compute/docs/labeling-resources
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter(name="lockConfig")
    def lock_config(self) -> pulumi.Output['outputs.LockConfigResponse']:
        """
        Optional. Configuration that indicates whether or not the Connection can be edited.
        """
        return pulumi.get(self, "lock_config")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Resource name of the Connection. Format: projects/{project}/locations/{location}/connections/{connection}
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> pulumi.Output[str]:
        """
        Optional. Service account needed for runtime plane to access GCP resources.
        """
        return pulumi.get(self, "service_account")

    @property
    @pulumi.getter(name="serviceDirectory")
    def service_directory(self) -> pulumi.Output[str]:
        """
        The name of the Service Directory service name. Used for Private Harpoon to resolve the ILB address. e.g. "projects/cloud-connectors-e2e-testing/locations/us-central1/namespaces/istio-system/services/istio-ingressgateway-connectors"
        """
        return pulumi.get(self, "service_directory")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output['outputs.ConnectionStatusResponse']:
        """
        Current status of the connection.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        Updated time.
        """
        return pulumi.get(self, "update_time")

