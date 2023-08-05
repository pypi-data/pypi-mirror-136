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
    'GetEndpointPolicyResult',
    'AwaitableGetEndpointPolicyResult',
    'get_endpoint_policy',
    'get_endpoint_policy_output',
]

@pulumi.output_type
class GetEndpointPolicyResult:
    def __init__(__self__, authorization_policy=None, client_tls_policy=None, create_time=None, description=None, endpoint_matcher=None, labels=None, name=None, server_tls_policy=None, traffic_port_selector=None, type=None, update_time=None):
        if authorization_policy and not isinstance(authorization_policy, str):
            raise TypeError("Expected argument 'authorization_policy' to be a str")
        pulumi.set(__self__, "authorization_policy", authorization_policy)
        if client_tls_policy and not isinstance(client_tls_policy, str):
            raise TypeError("Expected argument 'client_tls_policy' to be a str")
        pulumi.set(__self__, "client_tls_policy", client_tls_policy)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if endpoint_matcher and not isinstance(endpoint_matcher, dict):
            raise TypeError("Expected argument 'endpoint_matcher' to be a dict")
        pulumi.set(__self__, "endpoint_matcher", endpoint_matcher)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if server_tls_policy and not isinstance(server_tls_policy, str):
            raise TypeError("Expected argument 'server_tls_policy' to be a str")
        pulumi.set(__self__, "server_tls_policy", server_tls_policy)
        if traffic_port_selector and not isinstance(traffic_port_selector, dict):
            raise TypeError("Expected argument 'traffic_port_selector' to be a dict")
        pulumi.set(__self__, "traffic_port_selector", traffic_port_selector)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)

    @property
    @pulumi.getter(name="authorizationPolicy")
    def authorization_policy(self) -> str:
        """
        Optional. This field specifies the URL of AuthorizationPolicy resource that applies authorization policies to the inbound traffic at the matched endpoints. Refer to Authorization. If this field is not specified, authorization is disabled(no authz checks) for this endpoint.
        """
        return pulumi.get(self, "authorization_policy")

    @property
    @pulumi.getter(name="clientTlsPolicy")
    def client_tls_policy(self) -> str:
        """
        Optional. A URL referring to a ClientTlsPolicy resource. ClientTlsPolicy can be set to specify the authentication for traffic from the proxy to the actual endpoints. More specifically, it is applied to the outgoing traffic from the proxy to the endpoint. This is typically used for sidecar model where the proxy identifies itself as endpoint to the control plane, with the connection between sidecar and endpoint requiring authentication. If this field is not set, authentication is disabled(open). Applicable only when EndpointPolicyType is SIDECAR_PROXY.
        """
        return pulumi.get(self, "client_tls_policy")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The timestamp when the resource was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Optional. A free-text description of the resource. Max length 1024 characters.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="endpointMatcher")
    def endpoint_matcher(self) -> 'outputs.EndpointMatcherResponse':
        """
        A matcher that selects endpoints to which the policies should be applied.
        """
        return pulumi.get(self, "endpoint_matcher")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Optional. Set of label tags associated with the EndpointPolicy resource.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the EndpointPolicy resource. It matches pattern `projects/{project}/locations/global/endpointPolicies/{endpoint_policy}`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="serverTlsPolicy")
    def server_tls_policy(self) -> str:
        """
        Optional. A URL referring to ServerTlsPolicy resource. ServerTlsPolicy is used to determine the authentication policy to be applied to terminate the inbound traffic at the identified backends. If this field is not set, authentication is disabled(open) for this endpoint.
        """
        return pulumi.get(self, "server_tls_policy")

    @property
    @pulumi.getter(name="trafficPortSelector")
    def traffic_port_selector(self) -> 'outputs.TrafficPortSelectorResponse':
        """
        Optional. Port selector for the (matched) endpoints. If no port selector is provided, the matched config is applied to all ports.
        """
        return pulumi.get(self, "traffic_port_selector")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of endpoint policy. This is primarily used to validate the configuration.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        The timestamp when the resource was updated.
        """
        return pulumi.get(self, "update_time")


class AwaitableGetEndpointPolicyResult(GetEndpointPolicyResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetEndpointPolicyResult(
            authorization_policy=self.authorization_policy,
            client_tls_policy=self.client_tls_policy,
            create_time=self.create_time,
            description=self.description,
            endpoint_matcher=self.endpoint_matcher,
            labels=self.labels,
            name=self.name,
            server_tls_policy=self.server_tls_policy,
            traffic_port_selector=self.traffic_port_selector,
            type=self.type,
            update_time=self.update_time)


def get_endpoint_policy(endpoint_policy_id: Optional[str] = None,
                        location: Optional[str] = None,
                        project: Optional[str] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetEndpointPolicyResult:
    """
    Gets details of a single EndpointPolicy.
    """
    __args__ = dict()
    __args__['endpointPolicyId'] = endpoint_policy_id
    __args__['location'] = location
    __args__['project'] = project
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:networkservices/v1beta1:getEndpointPolicy', __args__, opts=opts, typ=GetEndpointPolicyResult).value

    return AwaitableGetEndpointPolicyResult(
        authorization_policy=__ret__.authorization_policy,
        client_tls_policy=__ret__.client_tls_policy,
        create_time=__ret__.create_time,
        description=__ret__.description,
        endpoint_matcher=__ret__.endpoint_matcher,
        labels=__ret__.labels,
        name=__ret__.name,
        server_tls_policy=__ret__.server_tls_policy,
        traffic_port_selector=__ret__.traffic_port_selector,
        type=__ret__.type,
        update_time=__ret__.update_time)


@_utilities.lift_output_func(get_endpoint_policy)
def get_endpoint_policy_output(endpoint_policy_id: Optional[pulumi.Input[str]] = None,
                               location: Optional[pulumi.Input[str]] = None,
                               project: Optional[pulumi.Input[Optional[str]]] = None,
                               opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetEndpointPolicyResult]:
    """
    Gets details of a single EndpointPolicy.
    """
    ...
