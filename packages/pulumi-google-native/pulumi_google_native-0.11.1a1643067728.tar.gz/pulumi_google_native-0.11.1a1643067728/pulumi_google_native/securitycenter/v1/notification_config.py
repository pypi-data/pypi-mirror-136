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

__all__ = ['NotificationConfigArgs', 'NotificationConfig']

@pulumi.input_type
class NotificationConfigArgs:
    def __init__(__self__, *,
                 config_id: pulumi.Input[str],
                 organization_id: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pubsub_topic: Optional[pulumi.Input[str]] = None,
                 streaming_config: Optional[pulumi.Input['StreamingConfigArgs']] = None):
        """
        The set of arguments for constructing a NotificationConfig resource.
        :param pulumi.Input[str] description: The description of the notification config (max of 1024 characters).
        :param pulumi.Input[str] name: The relative resource name of this notification config. See: https://cloud.google.com/apis/design/resource_names#relative_resource_name Example: "organizations/{organization_id}/notificationConfigs/notify_public_bucket".
        :param pulumi.Input[str] pubsub_topic: The Pub/Sub topic to send notifications to. Its format is "projects/[project_id]/topics/[topic]".
        :param pulumi.Input['StreamingConfigArgs'] streaming_config: The config for triggering streaming-based notifications.
        """
        pulumi.set(__self__, "config_id", config_id)
        pulumi.set(__self__, "organization_id", organization_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if pubsub_topic is not None:
            pulumi.set(__self__, "pubsub_topic", pubsub_topic)
        if streaming_config is not None:
            pulumi.set(__self__, "streaming_config", streaming_config)

    @property
    @pulumi.getter(name="configId")
    def config_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "config_id")

    @config_id.setter
    def config_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "config_id", value)

    @property
    @pulumi.getter(name="organizationId")
    def organization_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "organization_id")

    @organization_id.setter
    def organization_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "organization_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the notification config (max of 1024 characters).
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The relative resource name of this notification config. See: https://cloud.google.com/apis/design/resource_names#relative_resource_name Example: "organizations/{organization_id}/notificationConfigs/notify_public_bucket".
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="pubsubTopic")
    def pubsub_topic(self) -> Optional[pulumi.Input[str]]:
        """
        The Pub/Sub topic to send notifications to. Its format is "projects/[project_id]/topics/[topic]".
        """
        return pulumi.get(self, "pubsub_topic")

    @pubsub_topic.setter
    def pubsub_topic(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "pubsub_topic", value)

    @property
    @pulumi.getter(name="streamingConfig")
    def streaming_config(self) -> Optional[pulumi.Input['StreamingConfigArgs']]:
        """
        The config for triggering streaming-based notifications.
        """
        return pulumi.get(self, "streaming_config")

    @streaming_config.setter
    def streaming_config(self, value: Optional[pulumi.Input['StreamingConfigArgs']]):
        pulumi.set(self, "streaming_config", value)


class NotificationConfig(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 pubsub_topic: Optional[pulumi.Input[str]] = None,
                 streaming_config: Optional[pulumi.Input[pulumi.InputType['StreamingConfigArgs']]] = None,
                 __props__=None):
        """
        Creates a notification config.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: The description of the notification config (max of 1024 characters).
        :param pulumi.Input[str] name: The relative resource name of this notification config. See: https://cloud.google.com/apis/design/resource_names#relative_resource_name Example: "organizations/{organization_id}/notificationConfigs/notify_public_bucket".
        :param pulumi.Input[str] pubsub_topic: The Pub/Sub topic to send notifications to. Its format is "projects/[project_id]/topics/[topic]".
        :param pulumi.Input[pulumi.InputType['StreamingConfigArgs']] streaming_config: The config for triggering streaming-based notifications.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: NotificationConfigArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a notification config.

        :param str resource_name: The name of the resource.
        :param NotificationConfigArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(NotificationConfigArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 pubsub_topic: Optional[pulumi.Input[str]] = None,
                 streaming_config: Optional[pulumi.Input[pulumi.InputType['StreamingConfigArgs']]] = None,
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
            __props__ = NotificationConfigArgs.__new__(NotificationConfigArgs)

            if config_id is None and not opts.urn:
                raise TypeError("Missing required property 'config_id'")
            __props__.__dict__["config_id"] = config_id
            __props__.__dict__["description"] = description
            __props__.__dict__["name"] = name
            if organization_id is None and not opts.urn:
                raise TypeError("Missing required property 'organization_id'")
            __props__.__dict__["organization_id"] = organization_id
            __props__.__dict__["pubsub_topic"] = pubsub_topic
            __props__.__dict__["streaming_config"] = streaming_config
            __props__.__dict__["service_account"] = None
        super(NotificationConfig, __self__).__init__(
            'google-native:securitycenter/v1:NotificationConfig',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'NotificationConfig':
        """
        Get an existing NotificationConfig resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = NotificationConfigArgs.__new__(NotificationConfigArgs)

        __props__.__dict__["description"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["pubsub_topic"] = None
        __props__.__dict__["service_account"] = None
        __props__.__dict__["streaming_config"] = None
        return NotificationConfig(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        The description of the notification config (max of 1024 characters).
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The relative resource name of this notification config. See: https://cloud.google.com/apis/design/resource_names#relative_resource_name Example: "organizations/{organization_id}/notificationConfigs/notify_public_bucket".
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="pubsubTopic")
    def pubsub_topic(self) -> pulumi.Output[str]:
        """
        The Pub/Sub topic to send notifications to. Its format is "projects/[project_id]/topics/[topic]".
        """
        return pulumi.get(self, "pubsub_topic")

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> pulumi.Output[str]:
        """
        The service account that needs "pubsub.topics.publish" permission to publish to the Pub/Sub topic.
        """
        return pulumi.get(self, "service_account")

    @property
    @pulumi.getter(name="streamingConfig")
    def streaming_config(self) -> pulumi.Output['outputs.StreamingConfigResponse']:
        """
        The config for triggering streaming-based notifications.
        """
        return pulumi.get(self, "streaming_config")

