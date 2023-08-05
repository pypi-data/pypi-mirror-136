# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'V2AndroidApplicationArgs',
    'V2AndroidKeyRestrictionsArgs',
    'V2ApiTargetArgs',
    'V2BrowserKeyRestrictionsArgs',
    'V2IosKeyRestrictionsArgs',
    'V2RestrictionsArgs',
    'V2ServerKeyRestrictionsArgs',
]

@pulumi.input_type
class V2AndroidApplicationArgs:
    def __init__(__self__, *,
                 package_name: Optional[pulumi.Input[str]] = None,
                 sha1_fingerprint: Optional[pulumi.Input[str]] = None):
        """
        Identifier of an Android application for key use.
        :param pulumi.Input[str] package_name: The package name of the application.
        :param pulumi.Input[str] sha1_fingerprint: The SHA1 fingerprint of the application. For example, both sha1 formats are acceptable : DA:39:A3:EE:5E:6B:4B:0D:32:55:BF:EF:95:60:18:90:AF:D8:07:09 or DA39A3EE5E6B4B0D3255BFEF95601890AFD80709. Output format is the latter.
        """
        if package_name is not None:
            pulumi.set(__self__, "package_name", package_name)
        if sha1_fingerprint is not None:
            pulumi.set(__self__, "sha1_fingerprint", sha1_fingerprint)

    @property
    @pulumi.getter(name="packageName")
    def package_name(self) -> Optional[pulumi.Input[str]]:
        """
        The package name of the application.
        """
        return pulumi.get(self, "package_name")

    @package_name.setter
    def package_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "package_name", value)

    @property
    @pulumi.getter(name="sha1Fingerprint")
    def sha1_fingerprint(self) -> Optional[pulumi.Input[str]]:
        """
        The SHA1 fingerprint of the application. For example, both sha1 formats are acceptable : DA:39:A3:EE:5E:6B:4B:0D:32:55:BF:EF:95:60:18:90:AF:D8:07:09 or DA39A3EE5E6B4B0D3255BFEF95601890AFD80709. Output format is the latter.
        """
        return pulumi.get(self, "sha1_fingerprint")

    @sha1_fingerprint.setter
    def sha1_fingerprint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "sha1_fingerprint", value)


@pulumi.input_type
class V2AndroidKeyRestrictionsArgs:
    def __init__(__self__, *,
                 allowed_applications: Optional[pulumi.Input[Sequence[pulumi.Input['V2AndroidApplicationArgs']]]] = None):
        """
        The Android apps that are allowed to use the key.
        :param pulumi.Input[Sequence[pulumi.Input['V2AndroidApplicationArgs']]] allowed_applications: A list of Android applications that are allowed to make API calls with this key.
        """
        if allowed_applications is not None:
            pulumi.set(__self__, "allowed_applications", allowed_applications)

    @property
    @pulumi.getter(name="allowedApplications")
    def allowed_applications(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['V2AndroidApplicationArgs']]]]:
        """
        A list of Android applications that are allowed to make API calls with this key.
        """
        return pulumi.get(self, "allowed_applications")

    @allowed_applications.setter
    def allowed_applications(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['V2AndroidApplicationArgs']]]]):
        pulumi.set(self, "allowed_applications", value)


@pulumi.input_type
class V2ApiTargetArgs:
    def __init__(__self__, *,
                 methods: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 service: Optional[pulumi.Input[str]] = None):
        """
        A restriction for a specific service and optionally one or multiple specific methods. Both fields are case insensitive.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] methods: Optional. List of one or more methods that can be called. If empty, all methods for the service are allowed. A wildcard (*) can be used as the last symbol. Valid examples: `google.cloud.translate.v2.TranslateService.GetSupportedLanguage` `TranslateText` `Get*` `translate.googleapis.com.Get*`
        :param pulumi.Input[str] service: The service for this restriction. It should be the canonical service name, for example: `translate.googleapis.com`. You can use [`gcloud services list`](/sdk/gcloud/reference/services/list) to get a list of services that are enabled in the project.
        """
        if methods is not None:
            pulumi.set(__self__, "methods", methods)
        if service is not None:
            pulumi.set(__self__, "service", service)

    @property
    @pulumi.getter
    def methods(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Optional. List of one or more methods that can be called. If empty, all methods for the service are allowed. A wildcard (*) can be used as the last symbol. Valid examples: `google.cloud.translate.v2.TranslateService.GetSupportedLanguage` `TranslateText` `Get*` `translate.googleapis.com.Get*`
        """
        return pulumi.get(self, "methods")

    @methods.setter
    def methods(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "methods", value)

    @property
    @pulumi.getter
    def service(self) -> Optional[pulumi.Input[str]]:
        """
        The service for this restriction. It should be the canonical service name, for example: `translate.googleapis.com`. You can use [`gcloud services list`](/sdk/gcloud/reference/services/list) to get a list of services that are enabled in the project.
        """
        return pulumi.get(self, "service")

    @service.setter
    def service(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service", value)


@pulumi.input_type
class V2BrowserKeyRestrictionsArgs:
    def __init__(__self__, *,
                 allowed_referrers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The HTTP referrers (websites) that are allowed to use the key.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] allowed_referrers: A list of regular expressions for the referrer URLs that are allowed to make API calls with this key.
        """
        if allowed_referrers is not None:
            pulumi.set(__self__, "allowed_referrers", allowed_referrers)

    @property
    @pulumi.getter(name="allowedReferrers")
    def allowed_referrers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of regular expressions for the referrer URLs that are allowed to make API calls with this key.
        """
        return pulumi.get(self, "allowed_referrers")

    @allowed_referrers.setter
    def allowed_referrers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "allowed_referrers", value)


@pulumi.input_type
class V2IosKeyRestrictionsArgs:
    def __init__(__self__, *,
                 allowed_bundle_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The iOS apps that are allowed to use the key.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] allowed_bundle_ids: A list of bundle IDs that are allowed when making API calls with this key.
        """
        if allowed_bundle_ids is not None:
            pulumi.set(__self__, "allowed_bundle_ids", allowed_bundle_ids)

    @property
    @pulumi.getter(name="allowedBundleIds")
    def allowed_bundle_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of bundle IDs that are allowed when making API calls with this key.
        """
        return pulumi.get(self, "allowed_bundle_ids")

    @allowed_bundle_ids.setter
    def allowed_bundle_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "allowed_bundle_ids", value)


@pulumi.input_type
class V2RestrictionsArgs:
    def __init__(__self__, *,
                 android_key_restrictions: Optional[pulumi.Input['V2AndroidKeyRestrictionsArgs']] = None,
                 api_targets: Optional[pulumi.Input[Sequence[pulumi.Input['V2ApiTargetArgs']]]] = None,
                 browser_key_restrictions: Optional[pulumi.Input['V2BrowserKeyRestrictionsArgs']] = None,
                 ios_key_restrictions: Optional[pulumi.Input['V2IosKeyRestrictionsArgs']] = None,
                 server_key_restrictions: Optional[pulumi.Input['V2ServerKeyRestrictionsArgs']] = None):
        """
        Describes the restrictions on the key.
        :param pulumi.Input['V2AndroidKeyRestrictionsArgs'] android_key_restrictions: The Android apps that are allowed to use the key.
        :param pulumi.Input[Sequence[pulumi.Input['V2ApiTargetArgs']]] api_targets: A restriction for a specific service and optionally one or more specific methods. Requests are allowed if they match any of these restrictions. If no restrictions are specified, all targets are allowed.
        :param pulumi.Input['V2BrowserKeyRestrictionsArgs'] browser_key_restrictions: The HTTP referrers (websites) that are allowed to use the key.
        :param pulumi.Input['V2IosKeyRestrictionsArgs'] ios_key_restrictions: The iOS apps that are allowed to use the key.
        :param pulumi.Input['V2ServerKeyRestrictionsArgs'] server_key_restrictions: The IP addresses of callers that are allowed to use the key.
        """
        if android_key_restrictions is not None:
            pulumi.set(__self__, "android_key_restrictions", android_key_restrictions)
        if api_targets is not None:
            pulumi.set(__self__, "api_targets", api_targets)
        if browser_key_restrictions is not None:
            pulumi.set(__self__, "browser_key_restrictions", browser_key_restrictions)
        if ios_key_restrictions is not None:
            pulumi.set(__self__, "ios_key_restrictions", ios_key_restrictions)
        if server_key_restrictions is not None:
            pulumi.set(__self__, "server_key_restrictions", server_key_restrictions)

    @property
    @pulumi.getter(name="androidKeyRestrictions")
    def android_key_restrictions(self) -> Optional[pulumi.Input['V2AndroidKeyRestrictionsArgs']]:
        """
        The Android apps that are allowed to use the key.
        """
        return pulumi.get(self, "android_key_restrictions")

    @android_key_restrictions.setter
    def android_key_restrictions(self, value: Optional[pulumi.Input['V2AndroidKeyRestrictionsArgs']]):
        pulumi.set(self, "android_key_restrictions", value)

    @property
    @pulumi.getter(name="apiTargets")
    def api_targets(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['V2ApiTargetArgs']]]]:
        """
        A restriction for a specific service and optionally one or more specific methods. Requests are allowed if they match any of these restrictions. If no restrictions are specified, all targets are allowed.
        """
        return pulumi.get(self, "api_targets")

    @api_targets.setter
    def api_targets(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['V2ApiTargetArgs']]]]):
        pulumi.set(self, "api_targets", value)

    @property
    @pulumi.getter(name="browserKeyRestrictions")
    def browser_key_restrictions(self) -> Optional[pulumi.Input['V2BrowserKeyRestrictionsArgs']]:
        """
        The HTTP referrers (websites) that are allowed to use the key.
        """
        return pulumi.get(self, "browser_key_restrictions")

    @browser_key_restrictions.setter
    def browser_key_restrictions(self, value: Optional[pulumi.Input['V2BrowserKeyRestrictionsArgs']]):
        pulumi.set(self, "browser_key_restrictions", value)

    @property
    @pulumi.getter(name="iosKeyRestrictions")
    def ios_key_restrictions(self) -> Optional[pulumi.Input['V2IosKeyRestrictionsArgs']]:
        """
        The iOS apps that are allowed to use the key.
        """
        return pulumi.get(self, "ios_key_restrictions")

    @ios_key_restrictions.setter
    def ios_key_restrictions(self, value: Optional[pulumi.Input['V2IosKeyRestrictionsArgs']]):
        pulumi.set(self, "ios_key_restrictions", value)

    @property
    @pulumi.getter(name="serverKeyRestrictions")
    def server_key_restrictions(self) -> Optional[pulumi.Input['V2ServerKeyRestrictionsArgs']]:
        """
        The IP addresses of callers that are allowed to use the key.
        """
        return pulumi.get(self, "server_key_restrictions")

    @server_key_restrictions.setter
    def server_key_restrictions(self, value: Optional[pulumi.Input['V2ServerKeyRestrictionsArgs']]):
        pulumi.set(self, "server_key_restrictions", value)


@pulumi.input_type
class V2ServerKeyRestrictionsArgs:
    def __init__(__self__, *,
                 allowed_ips: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The IP addresses of callers that are allowed to use the key.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] allowed_ips: A list of the caller IP addresses that are allowed to make API calls with this key.
        """
        if allowed_ips is not None:
            pulumi.set(__self__, "allowed_ips", allowed_ips)

    @property
    @pulumi.getter(name="allowedIps")
    def allowed_ips(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of the caller IP addresses that are allowed to make API calls with this key.
        """
        return pulumi.get(self, "allowed_ips")

    @allowed_ips.setter
    def allowed_ips(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "allowed_ips", value)


