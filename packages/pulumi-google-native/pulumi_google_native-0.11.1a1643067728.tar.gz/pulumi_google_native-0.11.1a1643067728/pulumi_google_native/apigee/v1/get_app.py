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
    'GetAppResult',
    'AwaitableGetAppResult',
    'get_app',
    'get_app_output',
]

@pulumi.output_type
class GetAppResult:
    def __init__(__self__, api_products=None, app_family=None, app_id=None, attributes=None, callback_url=None, created_at=None, credentials=None, developer_id=None, key_expires_in=None, last_modified_at=None, name=None, scopes=None, status=None):
        if api_products and not isinstance(api_products, list):
            raise TypeError("Expected argument 'api_products' to be a list")
        pulumi.set(__self__, "api_products", api_products)
        if app_family and not isinstance(app_family, str):
            raise TypeError("Expected argument 'app_family' to be a str")
        pulumi.set(__self__, "app_family", app_family)
        if app_id and not isinstance(app_id, str):
            raise TypeError("Expected argument 'app_id' to be a str")
        pulumi.set(__self__, "app_id", app_id)
        if attributes and not isinstance(attributes, list):
            raise TypeError("Expected argument 'attributes' to be a list")
        pulumi.set(__self__, "attributes", attributes)
        if callback_url and not isinstance(callback_url, str):
            raise TypeError("Expected argument 'callback_url' to be a str")
        pulumi.set(__self__, "callback_url", callback_url)
        if created_at and not isinstance(created_at, str):
            raise TypeError("Expected argument 'created_at' to be a str")
        pulumi.set(__self__, "created_at", created_at)
        if credentials and not isinstance(credentials, list):
            raise TypeError("Expected argument 'credentials' to be a list")
        pulumi.set(__self__, "credentials", credentials)
        if developer_id and not isinstance(developer_id, str):
            raise TypeError("Expected argument 'developer_id' to be a str")
        pulumi.set(__self__, "developer_id", developer_id)
        if key_expires_in and not isinstance(key_expires_in, str):
            raise TypeError("Expected argument 'key_expires_in' to be a str")
        pulumi.set(__self__, "key_expires_in", key_expires_in)
        if last_modified_at and not isinstance(last_modified_at, str):
            raise TypeError("Expected argument 'last_modified_at' to be a str")
        pulumi.set(__self__, "last_modified_at", last_modified_at)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if scopes and not isinstance(scopes, list):
            raise TypeError("Expected argument 'scopes' to be a list")
        pulumi.set(__self__, "scopes", scopes)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="apiProducts")
    def api_products(self) -> Sequence[str]:
        """
        List of API products associated with the developer app.
        """
        return pulumi.get(self, "api_products")

    @property
    @pulumi.getter(name="appFamily")
    def app_family(self) -> str:
        """
        Developer app family.
        """
        return pulumi.get(self, "app_family")

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> str:
        """
        ID of the developer app.
        """
        return pulumi.get(self, "app_id")

    @property
    @pulumi.getter
    def attributes(self) -> Sequence['outputs.GoogleCloudApigeeV1AttributeResponse']:
        """
        List of attributes for the developer app.
        """
        return pulumi.get(self, "attributes")

    @property
    @pulumi.getter(name="callbackUrl")
    def callback_url(self) -> str:
        """
        Callback URL used by OAuth 2.0 authorization servers to communicate authorization codes back to developer apps.
        """
        return pulumi.get(self, "callback_url")

    @property
    @pulumi.getter(name="createdAt")
    def created_at(self) -> str:
        """
        Time the developer app was created in milliseconds since epoch.
        """
        return pulumi.get(self, "created_at")

    @property
    @pulumi.getter
    def credentials(self) -> Sequence['outputs.GoogleCloudApigeeV1CredentialResponse']:
        """
        Set of credentials for the developer app consisting of the consumer key/secret pairs associated with the API products.
        """
        return pulumi.get(self, "credentials")

    @property
    @pulumi.getter(name="developerId")
    def developer_id(self) -> str:
        """
        ID of the developer.
        """
        return pulumi.get(self, "developer_id")

    @property
    @pulumi.getter(name="keyExpiresIn")
    def key_expires_in(self) -> str:
        """
        Expiration time, in milliseconds, for the consumer key that is generated for the developer app. If not set or left to the default value of `-1`, the API key never expires. The expiration time can't be updated after it is set.
        """
        return pulumi.get(self, "key_expires_in")

    @property
    @pulumi.getter(name="lastModifiedAt")
    def last_modified_at(self) -> str:
        """
        Time the developer app was modified in milliseconds since epoch.
        """
        return pulumi.get(self, "last_modified_at")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the developer app.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def scopes(self) -> Sequence[str]:
        """
        Scopes to apply to the developer app. The specified scopes must already exist for the API product that you associate with the developer app.
        """
        return pulumi.get(self, "scopes")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of the credential. Valid values include `approved` or `revoked`.
        """
        return pulumi.get(self, "status")


class AwaitableGetAppResult(GetAppResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAppResult(
            api_products=self.api_products,
            app_family=self.app_family,
            app_id=self.app_id,
            attributes=self.attributes,
            callback_url=self.callback_url,
            created_at=self.created_at,
            credentials=self.credentials,
            developer_id=self.developer_id,
            key_expires_in=self.key_expires_in,
            last_modified_at=self.last_modified_at,
            name=self.name,
            scopes=self.scopes,
            status=self.status)


def get_app(app_id: Optional[str] = None,
            developer_id: Optional[str] = None,
            entity: Optional[str] = None,
            organization_id: Optional[str] = None,
            query: Optional[str] = None,
            opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAppResult:
    """
    Returns the details for a developer app.
    """
    __args__ = dict()
    __args__['appId'] = app_id
    __args__['developerId'] = developer_id
    __args__['entity'] = entity
    __args__['organizationId'] = organization_id
    __args__['query'] = query
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:apigee/v1:getApp', __args__, opts=opts, typ=GetAppResult).value

    return AwaitableGetAppResult(
        api_products=__ret__.api_products,
        app_family=__ret__.app_family,
        app_id=__ret__.app_id,
        attributes=__ret__.attributes,
        callback_url=__ret__.callback_url,
        created_at=__ret__.created_at,
        credentials=__ret__.credentials,
        developer_id=__ret__.developer_id,
        key_expires_in=__ret__.key_expires_in,
        last_modified_at=__ret__.last_modified_at,
        name=__ret__.name,
        scopes=__ret__.scopes,
        status=__ret__.status)


@_utilities.lift_output_func(get_app)
def get_app_output(app_id: Optional[pulumi.Input[str]] = None,
                   developer_id: Optional[pulumi.Input[str]] = None,
                   entity: Optional[pulumi.Input[Optional[str]]] = None,
                   organization_id: Optional[pulumi.Input[str]] = None,
                   query: Optional[pulumi.Input[Optional[str]]] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAppResult]:
    """
    Returns the details for a developer app.
    """
    ...
