# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from ._enums import *

__all__ = [
    'GoogleFirestoreAdminV1IndexFieldArgs',
]

@pulumi.input_type
class GoogleFirestoreAdminV1IndexFieldArgs:
    def __init__(__self__, *,
                 array_config: Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldArrayConfig']] = None,
                 field_path: Optional[pulumi.Input[str]] = None,
                 order: Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldOrder']] = None):
        """
        A field in an index. The field_path describes which field is indexed, the value_mode describes how the field value is indexed.
        :param pulumi.Input['GoogleFirestoreAdminV1IndexFieldArrayConfig'] array_config: Indicates that this field supports operations on `array_value`s.
        :param pulumi.Input[str] field_path: Can be __name__. For single field indexes, this must match the name of the field or may be omitted.
        :param pulumi.Input['GoogleFirestoreAdminV1IndexFieldOrder'] order: Indicates that this field supports ordering by the specified order or comparing using =, !=, <, <=, >, >=.
        """
        if array_config is not None:
            pulumi.set(__self__, "array_config", array_config)
        if field_path is not None:
            pulumi.set(__self__, "field_path", field_path)
        if order is not None:
            pulumi.set(__self__, "order", order)

    @property
    @pulumi.getter(name="arrayConfig")
    def array_config(self) -> Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldArrayConfig']]:
        """
        Indicates that this field supports operations on `array_value`s.
        """
        return pulumi.get(self, "array_config")

    @array_config.setter
    def array_config(self, value: Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldArrayConfig']]):
        pulumi.set(self, "array_config", value)

    @property
    @pulumi.getter(name="fieldPath")
    def field_path(self) -> Optional[pulumi.Input[str]]:
        """
        Can be __name__. For single field indexes, this must match the name of the field or may be omitted.
        """
        return pulumi.get(self, "field_path")

    @field_path.setter
    def field_path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "field_path", value)

    @property
    @pulumi.getter
    def order(self) -> Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldOrder']]:
        """
        Indicates that this field supports ordering by the specified order or comparing using =, !=, <, <=, >, >=.
        """
        return pulumi.get(self, "order")

    @order.setter
    def order(self, value: Optional[pulumi.Input['GoogleFirestoreAdminV1IndexFieldOrder']]):
        pulumi.set(self, "order", value)


