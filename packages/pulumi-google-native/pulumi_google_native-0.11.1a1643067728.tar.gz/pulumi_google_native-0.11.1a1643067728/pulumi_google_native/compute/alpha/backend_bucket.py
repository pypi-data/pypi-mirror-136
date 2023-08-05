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

__all__ = ['BackendBucketArgs', 'BackendBucket']

@pulumi.input_type
class BackendBucketArgs:
    def __init__(__self__, *,
                 bucket_name: Optional[pulumi.Input[str]] = None,
                 cdn_policy: Optional[pulumi.Input['BackendBucketCdnPolicyArgs']] = None,
                 compression_mode: Optional[pulumi.Input['BackendBucketCompressionMode']] = None,
                 custom_response_headers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enable_cdn: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a BackendBucket resource.
        :param pulumi.Input[str] bucket_name: Cloud Storage bucket name.
        :param pulumi.Input['BackendBucketCdnPolicyArgs'] cdn_policy: Cloud CDN configuration for this BackendBucket.
        :param pulumi.Input['BackendBucketCompressionMode'] compression_mode: Compress text responses using Brotli or gzip compression, based on the client's Accept-Encoding header.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] custom_response_headers: Headers that the HTTP/S load balancer should add to proxied responses.
        :param pulumi.Input[str] description: An optional textual description of the resource; provided by the client when the resource is created.
        :param pulumi.Input[bool] enable_cdn: If true, enable Cloud CDN for this BackendBucket.
        :param pulumi.Input[str] kind: Type of the resource.
        :param pulumi.Input[str] name: Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        if bucket_name is not None:
            pulumi.set(__self__, "bucket_name", bucket_name)
        if cdn_policy is not None:
            pulumi.set(__self__, "cdn_policy", cdn_policy)
        if compression_mode is not None:
            pulumi.set(__self__, "compression_mode", compression_mode)
        if custom_response_headers is not None:
            pulumi.set(__self__, "custom_response_headers", custom_response_headers)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if enable_cdn is not None:
            pulumi.set(__self__, "enable_cdn", enable_cdn)
        if kind is not None:
            pulumi.set(__self__, "kind", kind)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if request_id is not None:
            pulumi.set(__self__, "request_id", request_id)

    @property
    @pulumi.getter(name="bucketName")
    def bucket_name(self) -> Optional[pulumi.Input[str]]:
        """
        Cloud Storage bucket name.
        """
        return pulumi.get(self, "bucket_name")

    @bucket_name.setter
    def bucket_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bucket_name", value)

    @property
    @pulumi.getter(name="cdnPolicy")
    def cdn_policy(self) -> Optional[pulumi.Input['BackendBucketCdnPolicyArgs']]:
        """
        Cloud CDN configuration for this BackendBucket.
        """
        return pulumi.get(self, "cdn_policy")

    @cdn_policy.setter
    def cdn_policy(self, value: Optional[pulumi.Input['BackendBucketCdnPolicyArgs']]):
        pulumi.set(self, "cdn_policy", value)

    @property
    @pulumi.getter(name="compressionMode")
    def compression_mode(self) -> Optional[pulumi.Input['BackendBucketCompressionMode']]:
        """
        Compress text responses using Brotli or gzip compression, based on the client's Accept-Encoding header.
        """
        return pulumi.get(self, "compression_mode")

    @compression_mode.setter
    def compression_mode(self, value: Optional[pulumi.Input['BackendBucketCompressionMode']]):
        pulumi.set(self, "compression_mode", value)

    @property
    @pulumi.getter(name="customResponseHeaders")
    def custom_response_headers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Headers that the HTTP/S load balancer should add to proxied responses.
        """
        return pulumi.get(self, "custom_response_headers")

    @custom_response_headers.setter
    def custom_response_headers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "custom_response_headers", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        An optional textual description of the resource; provided by the client when the resource is created.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="enableCdn")
    def enable_cdn(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, enable Cloud CDN for this BackendBucket.
        """
        return pulumi.get(self, "enable_cdn")

    @enable_cdn.setter
    def enable_cdn(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enable_cdn", value)

    @property
    @pulumi.getter
    def kind(self) -> Optional[pulumi.Input[str]]:
        """
        Type of the resource.
        """
        return pulumi.get(self, "kind")

    @kind.setter
    def kind(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kind", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

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


class BackendBucket(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket_name: Optional[pulumi.Input[str]] = None,
                 cdn_policy: Optional[pulumi.Input[pulumi.InputType['BackendBucketCdnPolicyArgs']]] = None,
                 compression_mode: Optional[pulumi.Input['BackendBucketCompressionMode']] = None,
                 custom_response_headers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enable_cdn: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a BackendBucket resource in the specified project using the data included in the request.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bucket_name: Cloud Storage bucket name.
        :param pulumi.Input[pulumi.InputType['BackendBucketCdnPolicyArgs']] cdn_policy: Cloud CDN configuration for this BackendBucket.
        :param pulumi.Input['BackendBucketCompressionMode'] compression_mode: Compress text responses using Brotli or gzip compression, based on the client's Accept-Encoding header.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] custom_response_headers: Headers that the HTTP/S load balancer should add to proxied responses.
        :param pulumi.Input[str] description: An optional textual description of the resource; provided by the client when the resource is created.
        :param pulumi.Input[bool] enable_cdn: If true, enable Cloud CDN for this BackendBucket.
        :param pulumi.Input[str] kind: Type of the resource.
        :param pulumi.Input[str] name: Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[BackendBucketArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a BackendBucket resource in the specified project using the data included in the request.

        :param str resource_name: The name of the resource.
        :param BackendBucketArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(BackendBucketArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket_name: Optional[pulumi.Input[str]] = None,
                 cdn_policy: Optional[pulumi.Input[pulumi.InputType['BackendBucketCdnPolicyArgs']]] = None,
                 compression_mode: Optional[pulumi.Input['BackendBucketCompressionMode']] = None,
                 custom_response_headers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enable_cdn: Optional[pulumi.Input[bool]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = BackendBucketArgs.__new__(BackendBucketArgs)

            __props__.__dict__["bucket_name"] = bucket_name
            __props__.__dict__["cdn_policy"] = cdn_policy
            __props__.__dict__["compression_mode"] = compression_mode
            __props__.__dict__["custom_response_headers"] = custom_response_headers
            __props__.__dict__["description"] = description
            __props__.__dict__["enable_cdn"] = enable_cdn
            __props__.__dict__["kind"] = kind
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            __props__.__dict__["request_id"] = request_id
            __props__.__dict__["creation_timestamp"] = None
            __props__.__dict__["edge_security_policy"] = None
            __props__.__dict__["self_link"] = None
            __props__.__dict__["self_link_with_id"] = None
        super(BackendBucket, __self__).__init__(
            'google-native:compute/alpha:BackendBucket',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'BackendBucket':
        """
        Get an existing BackendBucket resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = BackendBucketArgs.__new__(BackendBucketArgs)

        __props__.__dict__["bucket_name"] = None
        __props__.__dict__["cdn_policy"] = None
        __props__.__dict__["compression_mode"] = None
        __props__.__dict__["creation_timestamp"] = None
        __props__.__dict__["custom_response_headers"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["edge_security_policy"] = None
        __props__.__dict__["enable_cdn"] = None
        __props__.__dict__["kind"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["self_link"] = None
        __props__.__dict__["self_link_with_id"] = None
        return BackendBucket(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="bucketName")
    def bucket_name(self) -> pulumi.Output[str]:
        """
        Cloud Storage bucket name.
        """
        return pulumi.get(self, "bucket_name")

    @property
    @pulumi.getter(name="cdnPolicy")
    def cdn_policy(self) -> pulumi.Output['outputs.BackendBucketCdnPolicyResponse']:
        """
        Cloud CDN configuration for this BackendBucket.
        """
        return pulumi.get(self, "cdn_policy")

    @property
    @pulumi.getter(name="compressionMode")
    def compression_mode(self) -> pulumi.Output[str]:
        """
        Compress text responses using Brotli or gzip compression, based on the client's Accept-Encoding header.
        """
        return pulumi.get(self, "compression_mode")

    @property
    @pulumi.getter(name="creationTimestamp")
    def creation_timestamp(self) -> pulumi.Output[str]:
        """
        Creation timestamp in RFC3339 text format.
        """
        return pulumi.get(self, "creation_timestamp")

    @property
    @pulumi.getter(name="customResponseHeaders")
    def custom_response_headers(self) -> pulumi.Output[Sequence[str]]:
        """
        Headers that the HTTP/S load balancer should add to proxied responses.
        """
        return pulumi.get(self, "custom_response_headers")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        An optional textual description of the resource; provided by the client when the resource is created.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="edgeSecurityPolicy")
    def edge_security_policy(self) -> pulumi.Output[str]:
        """
        The resource URL for the edge security policy associated with this backend bucket.
        """
        return pulumi.get(self, "edge_security_policy")

    @property
    @pulumi.getter(name="enableCdn")
    def enable_cdn(self) -> pulumi.Output[bool]:
        """
        If true, enable Cloud CDN for this BackendBucket.
        """
        return pulumi.get(self, "enable_cdn")

    @property
    @pulumi.getter
    def kind(self) -> pulumi.Output[str]:
        """
        Type of the resource.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> pulumi.Output[str]:
        """
        Server-defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter(name="selfLinkWithId")
    def self_link_with_id(self) -> pulumi.Output[str]:
        """
        Server-defined URL for this resource with the resource id.
        """
        return pulumi.get(self, "self_link_with_id")

