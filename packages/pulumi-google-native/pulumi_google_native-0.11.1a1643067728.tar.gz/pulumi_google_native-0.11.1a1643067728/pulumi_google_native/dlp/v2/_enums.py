# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'GooglePrivacyDlpV2BigQueryOptionsSampleMethod',
    'GooglePrivacyDlpV2CharsToIgnoreCommonCharactersToIgnore',
    'GooglePrivacyDlpV2CloudStorageOptionsFileTypesItem',
    'GooglePrivacyDlpV2CloudStorageOptionsSampleMethod',
    'GooglePrivacyDlpV2ConditionOperator',
    'GooglePrivacyDlpV2CryptoReplaceFfxFpeConfigCommonAlphabet',
    'GooglePrivacyDlpV2CustomInfoTypeExclusionType',
    'GooglePrivacyDlpV2CustomInfoTypeLikelihood',
    'GooglePrivacyDlpV2ExclusionRuleMatchingType',
    'GooglePrivacyDlpV2ExpressionsLogicalOperator',
    'GooglePrivacyDlpV2InspectConfigMinLikelihood',
    'GooglePrivacyDlpV2LikelihoodAdjustmentFixedLikelihood',
    'GooglePrivacyDlpV2OutputStorageConfigOutputSchema',
    'GooglePrivacyDlpV2TimePartConfigPartToExtract',
    'GooglePrivacyDlpV2ValueDayOfWeekValue',
    'JobTriggerStatus',
]


class GooglePrivacyDlpV2BigQueryOptionsSampleMethod(str, Enum):
    SAMPLE_METHOD_UNSPECIFIED = "SAMPLE_METHOD_UNSPECIFIED"
    TOP = "TOP"
    """
    Scan groups of rows in the order BigQuery provides (default). Multiple groups of rows may be scanned in parallel, so results may not appear in the same order the rows are read.
    """
    RANDOM_START = "RANDOM_START"
    """
    Randomly pick groups of rows to scan.
    """


class GooglePrivacyDlpV2CharsToIgnoreCommonCharactersToIgnore(str, Enum):
    """
    Common characters to not transform when masking. Useful to avoid removing punctuation.
    """
    COMMON_CHARS_TO_IGNORE_UNSPECIFIED = "COMMON_CHARS_TO_IGNORE_UNSPECIFIED"
    """
    Unused.
    """
    NUMERIC = "NUMERIC"
    """
    0-9
    """
    ALPHA_UPPER_CASE = "ALPHA_UPPER_CASE"
    """
    A-Z
    """
    ALPHA_LOWER_CASE = "ALPHA_LOWER_CASE"
    """
    a-z
    """
    PUNCTUATION = "PUNCTUATION"
    """
    US Punctuation, one of !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    """
    WHITESPACE = "WHITESPACE"
    """
    Whitespace character, one of [ \t\n\\x0B\f\r]
    """


class GooglePrivacyDlpV2CloudStorageOptionsFileTypesItem(str, Enum):
    FILE_TYPE_UNSPECIFIED = "FILE_TYPE_UNSPECIFIED"
    """
    Includes all files.
    """
    BINARY_FILE = "BINARY_FILE"
    """
    Includes all file extensions not covered by another entry. Binary scanning attempts to convert the content of the file to utf_8 to scan the file. If you wish to avoid this fall back, specify one or more of the other FileType's in your storage scan.
    """
    TEXT_FILE = "TEXT_FILE"
    """
    Included file extensions: asc,asp, aspx, brf, c, cc,cfm, cgi, cpp, csv, cxx, c++, cs, css, dart, dat, dot, eml,, epbub, ged, go, h, hh, hpp, hxx, h++, hs, html, htm, mkd, markdown, m, ml, mli, perl, pl, plist, pm, php, phtml, pht, properties, py, pyw, rb, rbw, rs, rss, rc, scala, sh, sql, swift, tex, shtml, shtm, xhtml, lhs, ics, ini, java, js, json, kix, kml, ocaml, md, txt, text, tsv, vb, vcard, vcs, wml, xcodeproj, xml, xsl, xsd, yml, yaml.
    """
    IMAGE = "IMAGE"
    """
    Included file extensions: bmp, gif, jpg, jpeg, jpe, png. bytes_limit_per_file has no effect on image files. Image inspection is restricted to 'global', 'us', 'asia', and 'europe'.
    """
    WORD = "WORD"
    """
    Word files >30 MB will be scanned as binary files. Included file extensions: docx, dotx, docm, dotm
    """
    PDF = "PDF"
    """
    PDF files >30 MB will be scanned as binary files. Included file extensions: pdf
    """
    AVRO = "AVRO"
    """
    Included file extensions: avro
    """
    CSV = "CSV"
    """
    Included file extensions: csv
    """
    TSV = "TSV"
    """
    Included file extensions: tsv
    """


class GooglePrivacyDlpV2CloudStorageOptionsSampleMethod(str, Enum):
    SAMPLE_METHOD_UNSPECIFIED = "SAMPLE_METHOD_UNSPECIFIED"
    TOP = "TOP"
    """
    Scan from the top (default).
    """
    RANDOM_START = "RANDOM_START"
    """
    For each file larger than bytes_limit_per_file, randomly pick the offset to start scanning. The scanned bytes are contiguous.
    """


class GooglePrivacyDlpV2ConditionOperator(str, Enum):
    """
    Required. Operator used to compare the field or infoType to the value.
    """
    RELATIONAL_OPERATOR_UNSPECIFIED = "RELATIONAL_OPERATOR_UNSPECIFIED"
    """
    Unused
    """
    EQUAL_TO = "EQUAL_TO"
    """
    Equal. Attempts to match even with incompatible types.
    """
    NOT_EQUAL_TO = "NOT_EQUAL_TO"
    """
    Not equal to. Attempts to match even with incompatible types.
    """
    GREATER_THAN = "GREATER_THAN"
    """
    Greater than.
    """
    LESS_THAN = "LESS_THAN"
    """
    Less than.
    """
    GREATER_THAN_OR_EQUALS = "GREATER_THAN_OR_EQUALS"
    """
    Greater than or equals.
    """
    LESS_THAN_OR_EQUALS = "LESS_THAN_OR_EQUALS"
    """
    Less than or equals.
    """
    EXISTS = "EXISTS"
    """
    Exists
    """


class GooglePrivacyDlpV2CryptoReplaceFfxFpeConfigCommonAlphabet(str, Enum):
    """
    Common alphabets.
    """
    FFX_COMMON_NATIVE_ALPHABET_UNSPECIFIED = "FFX_COMMON_NATIVE_ALPHABET_UNSPECIFIED"
    """
    Unused.
    """
    NUMERIC = "NUMERIC"
    """
    `[0-9]` (radix of 10)
    """
    HEXADECIMAL = "HEXADECIMAL"
    """
    `[0-9A-F]` (radix of 16)
    """
    UPPER_CASE_ALPHA_NUMERIC = "UPPER_CASE_ALPHA_NUMERIC"
    """
    `[0-9A-Z]` (radix of 36)
    """
    ALPHA_NUMERIC = "ALPHA_NUMERIC"
    """
    `[0-9A-Za-z]` (radix of 62)
    """


class GooglePrivacyDlpV2CustomInfoTypeExclusionType(str, Enum):
    """
    If set to EXCLUSION_TYPE_EXCLUDE this infoType will not cause a finding to be returned. It still can be used for rules matching.
    """
    EXCLUSION_TYPE_UNSPECIFIED = "EXCLUSION_TYPE_UNSPECIFIED"
    """
    A finding of this custom info type will not be excluded from results.
    """
    EXCLUSION_TYPE_EXCLUDE = "EXCLUSION_TYPE_EXCLUDE"
    """
    A finding of this custom info type will be excluded from final results, but can still affect rule execution.
    """


class GooglePrivacyDlpV2CustomInfoTypeLikelihood(str, Enum):
    """
    Likelihood to return for this CustomInfoType. This base value can be altered by a detection rule if the finding meets the criteria specified by the rule. Defaults to `VERY_LIKELY` if not specified.
    """
    LIKELIHOOD_UNSPECIFIED = "LIKELIHOOD_UNSPECIFIED"
    """
    Default value; same as POSSIBLE.
    """
    VERY_UNLIKELY = "VERY_UNLIKELY"
    """
    Few matching elements.
    """
    UNLIKELY = "UNLIKELY"
    POSSIBLE = "POSSIBLE"
    """
    Some matching elements.
    """
    LIKELY = "LIKELY"
    VERY_LIKELY = "VERY_LIKELY"
    """
    Many matching elements.
    """


class GooglePrivacyDlpV2ExclusionRuleMatchingType(str, Enum):
    """
    How the rule is applied, see MatchingType documentation for details.
    """
    MATCHING_TYPE_UNSPECIFIED = "MATCHING_TYPE_UNSPECIFIED"
    """
    Invalid.
    """
    MATCHING_TYPE_FULL_MATCH = "MATCHING_TYPE_FULL_MATCH"
    """
    Full match. - Dictionary: join of Dictionary results matched complete finding quote - Regex: all regex matches fill a finding quote start to end - Exclude info type: completely inside affecting info types findings
    """
    MATCHING_TYPE_PARTIAL_MATCH = "MATCHING_TYPE_PARTIAL_MATCH"
    """
    Partial match. - Dictionary: at least one of the tokens in the finding matches - Regex: substring of the finding matches - Exclude info type: intersects with affecting info types findings
    """
    MATCHING_TYPE_INVERSE_MATCH = "MATCHING_TYPE_INVERSE_MATCH"
    """
    Inverse match. - Dictionary: no tokens in the finding match the dictionary - Regex: finding doesn't match the regex - Exclude info type: no intersection with affecting info types findings
    """


class GooglePrivacyDlpV2ExpressionsLogicalOperator(str, Enum):
    """
    The operator to apply to the result of conditions. Default and currently only supported value is `AND`.
    """
    LOGICAL_OPERATOR_UNSPECIFIED = "LOGICAL_OPERATOR_UNSPECIFIED"
    """
    Unused
    """
    AND_ = "AND"
    """
    Conditional AND
    """


class GooglePrivacyDlpV2InspectConfigMinLikelihood(str, Enum):
    """
    Only returns findings equal or above this threshold. The default is POSSIBLE. See https://cloud.google.com/dlp/docs/likelihood to learn more.
    """
    LIKELIHOOD_UNSPECIFIED = "LIKELIHOOD_UNSPECIFIED"
    """
    Default value; same as POSSIBLE.
    """
    VERY_UNLIKELY = "VERY_UNLIKELY"
    """
    Few matching elements.
    """
    UNLIKELY = "UNLIKELY"
    POSSIBLE = "POSSIBLE"
    """
    Some matching elements.
    """
    LIKELY = "LIKELY"
    VERY_LIKELY = "VERY_LIKELY"
    """
    Many matching elements.
    """


class GooglePrivacyDlpV2LikelihoodAdjustmentFixedLikelihood(str, Enum):
    """
    Set the likelihood of a finding to a fixed value.
    """
    LIKELIHOOD_UNSPECIFIED = "LIKELIHOOD_UNSPECIFIED"
    """
    Default value; same as POSSIBLE.
    """
    VERY_UNLIKELY = "VERY_UNLIKELY"
    """
    Few matching elements.
    """
    UNLIKELY = "UNLIKELY"
    POSSIBLE = "POSSIBLE"
    """
    Some matching elements.
    """
    LIKELY = "LIKELY"
    VERY_LIKELY = "VERY_LIKELY"
    """
    Many matching elements.
    """


class GooglePrivacyDlpV2OutputStorageConfigOutputSchema(str, Enum):
    """
    Schema used for writing the findings for Inspect jobs. This field is only used for Inspect and must be unspecified for Risk jobs. Columns are derived from the `Finding` object. If appending to an existing table, any columns from the predefined schema that are missing will be added. No columns in the existing table will be deleted. If unspecified, then all available columns will be used for a new table or an (existing) table with no schema, and no changes will be made to an existing table that has a schema. Only for use with external storage.
    """
    OUTPUT_SCHEMA_UNSPECIFIED = "OUTPUT_SCHEMA_UNSPECIFIED"
    """
    Unused.
    """
    BASIC_COLUMNS = "BASIC_COLUMNS"
    """
    Basic schema including only `info_type`, `quote`, `certainty`, and `timestamp`.
    """
    GCS_COLUMNS = "GCS_COLUMNS"
    """
    Schema tailored to findings from scanning Google Cloud Storage.
    """
    DATASTORE_COLUMNS = "DATASTORE_COLUMNS"
    """
    Schema tailored to findings from scanning Google Datastore.
    """
    BIG_QUERY_COLUMNS = "BIG_QUERY_COLUMNS"
    """
    Schema tailored to findings from scanning Google BigQuery.
    """
    ALL_COLUMNS = "ALL_COLUMNS"
    """
    Schema containing all columns.
    """


class GooglePrivacyDlpV2TimePartConfigPartToExtract(str, Enum):
    """
    The part of the time to keep.
    """
    TIME_PART_UNSPECIFIED = "TIME_PART_UNSPECIFIED"
    """
    Unused
    """
    YEAR = "YEAR"
    """
    [0-9999]
    """
    MONTH = "MONTH"
    """
    [1-12]
    """
    DAY_OF_MONTH = "DAY_OF_MONTH"
    """
    [1-31]
    """
    DAY_OF_WEEK = "DAY_OF_WEEK"
    """
    [1-7]
    """
    WEEK_OF_YEAR = "WEEK_OF_YEAR"
    """
    [1-53]
    """
    HOUR_OF_DAY = "HOUR_OF_DAY"
    """
    [0-23]
    """


class GooglePrivacyDlpV2ValueDayOfWeekValue(str, Enum):
    """
    day of week
    """
    DAY_OF_WEEK_UNSPECIFIED = "DAY_OF_WEEK_UNSPECIFIED"
    """
    The day of the week is unspecified.
    """
    MONDAY = "MONDAY"
    """
    Monday
    """
    TUESDAY = "TUESDAY"
    """
    Tuesday
    """
    WEDNESDAY = "WEDNESDAY"
    """
    Wednesday
    """
    THURSDAY = "THURSDAY"
    """
    Thursday
    """
    FRIDAY = "FRIDAY"
    """
    Friday
    """
    SATURDAY = "SATURDAY"
    """
    Saturday
    """
    SUNDAY = "SUNDAY"
    """
    Sunday
    """


class JobTriggerStatus(str, Enum):
    """
    Required. A status for this trigger.
    """
    STATUS_UNSPECIFIED = "STATUS_UNSPECIFIED"
    """
    Unused.
    """
    HEALTHY = "HEALTHY"
    """
    Trigger is healthy.
    """
    PAUSED = "PAUSED"
    """
    Trigger is temporarily paused.
    """
    CANCELLED = "CANCELLED"
    """
    Trigger is cancelled and can not be resumed.
    """
