# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'GcsSourceArgs',
    'GlossaryInputConfigArgs',
    'LanguageCodePairArgs',
    'LanguageCodesSetArgs',
]

@pulumi.input_type
class GcsSourceArgs:
    def __init__(__self__, *,
                 input_uri: pulumi.Input[str]):
        """
        The Google Cloud Storage location for the input content.
        :param pulumi.Input[str] input_uri: Source data URI. For example, `gs://my_bucket/my_object`.
        """
        pulumi.set(__self__, "input_uri", input_uri)

    @property
    @pulumi.getter(name="inputUri")
    def input_uri(self) -> pulumi.Input[str]:
        """
        Source data URI. For example, `gs://my_bucket/my_object`.
        """
        return pulumi.get(self, "input_uri")

    @input_uri.setter
    def input_uri(self, value: pulumi.Input[str]):
        pulumi.set(self, "input_uri", value)


@pulumi.input_type
class GlossaryInputConfigArgs:
    def __init__(__self__, *,
                 gcs_source: pulumi.Input['GcsSourceArgs']):
        """
        Input configuration for glossaries.
        :param pulumi.Input['GcsSourceArgs'] gcs_source: Google Cloud Storage location of glossary data. File format is determined based on the filename extension. API returns [google.rpc.Code.INVALID_ARGUMENT] for unsupported URI-s and file formats. Wildcards are not allowed. This must be a single file in one of the following formats: For unidirectional glossaries: - TSV/CSV (`.tsv`/`.csv`): 2 column file, tab- or comma-separated. The first column is source text. The second column is target text. The file must not contain headers. That is, the first row is data, not column names. - TMX (`.tmx`): TMX file with parallel data defining source/target term pairs. For equivalent term sets glossaries: - CSV (`.csv`): Multi-column CSV file defining equivalent glossary terms in multiple languages. See documentation for more information - [glossaries](https://cloud.google.com/translate/docs/advanced/glossary).
        """
        pulumi.set(__self__, "gcs_source", gcs_source)

    @property
    @pulumi.getter(name="gcsSource")
    def gcs_source(self) -> pulumi.Input['GcsSourceArgs']:
        """
        Google Cloud Storage location of glossary data. File format is determined based on the filename extension. API returns [google.rpc.Code.INVALID_ARGUMENT] for unsupported URI-s and file formats. Wildcards are not allowed. This must be a single file in one of the following formats: For unidirectional glossaries: - TSV/CSV (`.tsv`/`.csv`): 2 column file, tab- or comma-separated. The first column is source text. The second column is target text. The file must not contain headers. That is, the first row is data, not column names. - TMX (`.tmx`): TMX file with parallel data defining source/target term pairs. For equivalent term sets glossaries: - CSV (`.csv`): Multi-column CSV file defining equivalent glossary terms in multiple languages. See documentation for more information - [glossaries](https://cloud.google.com/translate/docs/advanced/glossary).
        """
        return pulumi.get(self, "gcs_source")

    @gcs_source.setter
    def gcs_source(self, value: pulumi.Input['GcsSourceArgs']):
        pulumi.set(self, "gcs_source", value)


@pulumi.input_type
class LanguageCodePairArgs:
    def __init__(__self__, *,
                 source_language_code: pulumi.Input[str],
                 target_language_code: pulumi.Input[str]):
        """
        Used with unidirectional glossaries.
        :param pulumi.Input[str] source_language_code: The BCP-47 language code of the input text, for example, "en-US". Expected to be an exact match for GlossaryTerm.language_code.
        :param pulumi.Input[str] target_language_code: The BCP-47 language code for translation output, for example, "zh-CN". Expected to be an exact match for GlossaryTerm.language_code.
        """
        pulumi.set(__self__, "source_language_code", source_language_code)
        pulumi.set(__self__, "target_language_code", target_language_code)

    @property
    @pulumi.getter(name="sourceLanguageCode")
    def source_language_code(self) -> pulumi.Input[str]:
        """
        The BCP-47 language code of the input text, for example, "en-US". Expected to be an exact match for GlossaryTerm.language_code.
        """
        return pulumi.get(self, "source_language_code")

    @source_language_code.setter
    def source_language_code(self, value: pulumi.Input[str]):
        pulumi.set(self, "source_language_code", value)

    @property
    @pulumi.getter(name="targetLanguageCode")
    def target_language_code(self) -> pulumi.Input[str]:
        """
        The BCP-47 language code for translation output, for example, "zh-CN". Expected to be an exact match for GlossaryTerm.language_code.
        """
        return pulumi.get(self, "target_language_code")

    @target_language_code.setter
    def target_language_code(self, value: pulumi.Input[str]):
        pulumi.set(self, "target_language_code", value)


@pulumi.input_type
class LanguageCodesSetArgs:
    def __init__(__self__, *,
                 language_codes: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Used with equivalent term set glossaries.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] language_codes: The BCP-47 language code(s) for terms defined in the glossary. All entries are unique. The list contains at least two entries. Expected to be an exact match for GlossaryTerm.language_code.
        """
        if language_codes is not None:
            pulumi.set(__self__, "language_codes", language_codes)

    @property
    @pulumi.getter(name="languageCodes")
    def language_codes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The BCP-47 language code(s) for terms defined in the glossary. All entries are unique. The list contains at least two entries. Expected to be an exact match for GlossaryTerm.language_code.
        """
        return pulumi.get(self, "language_codes")

    @language_codes.setter
    def language_codes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "language_codes", value)


