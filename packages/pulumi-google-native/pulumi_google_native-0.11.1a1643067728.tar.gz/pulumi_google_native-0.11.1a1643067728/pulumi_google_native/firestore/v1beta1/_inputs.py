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
    'GoogleFirestoreAdminV1beta1IndexFieldArgs',
]

@pulumi.input_type
class GoogleFirestoreAdminV1beta1IndexFieldArgs:
    def __init__(__self__, *,
                 field_path: Optional[pulumi.Input[str]] = None,
                 mode: Optional[pulumi.Input['GoogleFirestoreAdminV1beta1IndexFieldMode']] = None):
        """
        A field of an index.
        :param pulumi.Input[str] field_path: The path of the field. Must match the field path specification described by google.firestore.v1beta1.Document.fields. Special field path `__name__` may be used by itself or at the end of a path. `__type__` may be used only at the end of path.
        :param pulumi.Input['GoogleFirestoreAdminV1beta1IndexFieldMode'] mode: The field's mode.
        """
        if field_path is not None:
            pulumi.set(__self__, "field_path", field_path)
        if mode is not None:
            pulumi.set(__self__, "mode", mode)

    @property
    @pulumi.getter(name="fieldPath")
    def field_path(self) -> Optional[pulumi.Input[str]]:
        """
        The path of the field. Must match the field path specification described by google.firestore.v1beta1.Document.fields. Special field path `__name__` may be used by itself or at the end of a path. `__type__` may be used only at the end of path.
        """
        return pulumi.get(self, "field_path")

    @field_path.setter
    def field_path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "field_path", value)

    @property
    @pulumi.getter
    def mode(self) -> Optional[pulumi.Input['GoogleFirestoreAdminV1beta1IndexFieldMode']]:
        """
        The field's mode.
        """
        return pulumi.get(self, "mode")

    @mode.setter
    def mode(self, value: Optional[pulumi.Input['GoogleFirestoreAdminV1beta1IndexFieldMode']]):
        pulumi.set(self, "mode", value)


