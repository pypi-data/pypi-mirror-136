# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'ModelStateArgs',
    'TfLiteModelArgs',
]

@pulumi.input_type
class ModelStateArgs:
    def __init__(__self__, *,
                 published: Optional[pulumi.Input[bool]] = None):
        """
        State common to all model types. Includes publishing and validation information.
        :param pulumi.Input[bool] published: Indicates if this model has been published.
        """
        if published is not None:
            pulumi.set(__self__, "published", published)

    @property
    @pulumi.getter
    def published(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if this model has been published.
        """
        return pulumi.get(self, "published")

    @published.setter
    def published(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "published", value)


@pulumi.input_type
class TfLiteModelArgs:
    def __init__(__self__, *,
                 automl_model: Optional[pulumi.Input[str]] = None,
                 gcs_tflite_uri: Optional[pulumi.Input[str]] = None):
        """
        Information that is specific to TfLite models.
        :param pulumi.Input[str] automl_model: The AutoML model id referencing a model you created with the AutoML API. The name should have format 'projects//locations//models/' (This is the model resource name returned from the AutoML API)
        :param pulumi.Input[str] gcs_tflite_uri: The TfLite file containing the model. (Stored in Google Cloud). The gcs_tflite_uri should have form: gs://some-bucket/some-model.tflite Note: If you update the file in the original location, it is necessary to call UpdateModel for ML to pick up and validate the updated file.
        """
        if automl_model is not None:
            pulumi.set(__self__, "automl_model", automl_model)
        if gcs_tflite_uri is not None:
            pulumi.set(__self__, "gcs_tflite_uri", gcs_tflite_uri)

    @property
    @pulumi.getter(name="automlModel")
    def automl_model(self) -> Optional[pulumi.Input[str]]:
        """
        The AutoML model id referencing a model you created with the AutoML API. The name should have format 'projects//locations//models/' (This is the model resource name returned from the AutoML API)
        """
        return pulumi.get(self, "automl_model")

    @automl_model.setter
    def automl_model(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "automl_model", value)

    @property
    @pulumi.getter(name="gcsTfliteUri")
    def gcs_tflite_uri(self) -> Optional[pulumi.Input[str]]:
        """
        The TfLite file containing the model. (Stored in Google Cloud). The gcs_tflite_uri should have form: gs://some-bucket/some-model.tflite Note: If you update the file in the original location, it is necessary to call UpdateModel for ML to pick up and validate the updated file.
        """
        return pulumi.get(self, "gcs_tflite_uri")

    @gcs_tflite_uri.setter
    def gcs_tflite_uri(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "gcs_tflite_uri", value)


