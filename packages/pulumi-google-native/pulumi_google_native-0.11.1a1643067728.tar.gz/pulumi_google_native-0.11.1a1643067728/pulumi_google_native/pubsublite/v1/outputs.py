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

__all__ = [
    'CapacityResponse',
    'DeliveryConfigResponse',
    'PartitionConfigResponse',
    'ReservationConfigResponse',
    'RetentionConfigResponse',
]

@pulumi.output_type
class CapacityResponse(dict):
    """
    The throughput capacity configuration for each partition.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "publishMibPerSec":
            suggest = "publish_mib_per_sec"
        elif key == "subscribeMibPerSec":
            suggest = "subscribe_mib_per_sec"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in CapacityResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        CapacityResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        CapacityResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 publish_mib_per_sec: int,
                 subscribe_mib_per_sec: int):
        """
        The throughput capacity configuration for each partition.
        :param int publish_mib_per_sec: Publish throughput capacity per partition in MiB/s. Must be >= 4 and <= 16.
        :param int subscribe_mib_per_sec: Subscribe throughput capacity per partition in MiB/s. Must be >= 4 and <= 32.
        """
        pulumi.set(__self__, "publish_mib_per_sec", publish_mib_per_sec)
        pulumi.set(__self__, "subscribe_mib_per_sec", subscribe_mib_per_sec)

    @property
    @pulumi.getter(name="publishMibPerSec")
    def publish_mib_per_sec(self) -> int:
        """
        Publish throughput capacity per partition in MiB/s. Must be >= 4 and <= 16.
        """
        return pulumi.get(self, "publish_mib_per_sec")

    @property
    @pulumi.getter(name="subscribeMibPerSec")
    def subscribe_mib_per_sec(self) -> int:
        """
        Subscribe throughput capacity per partition in MiB/s. Must be >= 4 and <= 32.
        """
        return pulumi.get(self, "subscribe_mib_per_sec")


@pulumi.output_type
class DeliveryConfigResponse(dict):
    """
    The settings for a subscription's message delivery.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "deliveryRequirement":
            suggest = "delivery_requirement"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DeliveryConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DeliveryConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DeliveryConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 delivery_requirement: str):
        """
        The settings for a subscription's message delivery.
        :param str delivery_requirement: The DeliveryRequirement for this subscription.
        """
        pulumi.set(__self__, "delivery_requirement", delivery_requirement)

    @property
    @pulumi.getter(name="deliveryRequirement")
    def delivery_requirement(self) -> str:
        """
        The DeliveryRequirement for this subscription.
        """
        return pulumi.get(self, "delivery_requirement")


@pulumi.output_type
class PartitionConfigResponse(dict):
    """
    The settings for a topic's partitions.
    """
    def __init__(__self__, *,
                 capacity: 'outputs.CapacityResponse',
                 count: str):
        """
        The settings for a topic's partitions.
        :param 'CapacityResponse' capacity: The capacity configuration.
        :param str count: The number of partitions in the topic. Must be at least 1. Once a topic has been created the number of partitions can be increased but not decreased. Message ordering is not guaranteed across a topic resize. For more information see https://cloud.google.com/pubsub/lite/docs/topics#scaling_capacity
        """
        pulumi.set(__self__, "capacity", capacity)
        pulumi.set(__self__, "count", count)

    @property
    @pulumi.getter
    def capacity(self) -> 'outputs.CapacityResponse':
        """
        The capacity configuration.
        """
        return pulumi.get(self, "capacity")

    @property
    @pulumi.getter
    def count(self) -> str:
        """
        The number of partitions in the topic. Must be at least 1. Once a topic has been created the number of partitions can be increased but not decreased. Message ordering is not guaranteed across a topic resize. For more information see https://cloud.google.com/pubsub/lite/docs/topics#scaling_capacity
        """
        return pulumi.get(self, "count")


@pulumi.output_type
class ReservationConfigResponse(dict):
    """
    The settings for this topic's Reservation usage.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "throughputReservation":
            suggest = "throughput_reservation"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in ReservationConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        ReservationConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        ReservationConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 throughput_reservation: str):
        """
        The settings for this topic's Reservation usage.
        :param str throughput_reservation: The Reservation to use for this topic's throughput capacity. Structured like: projects/{project_number}/locations/{location}/reservations/{reservation_id}
        """
        pulumi.set(__self__, "throughput_reservation", throughput_reservation)

    @property
    @pulumi.getter(name="throughputReservation")
    def throughput_reservation(self) -> str:
        """
        The Reservation to use for this topic's throughput capacity. Structured like: projects/{project_number}/locations/{location}/reservations/{reservation_id}
        """
        return pulumi.get(self, "throughput_reservation")


@pulumi.output_type
class RetentionConfigResponse(dict):
    """
    The settings for a topic's message retention.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "perPartitionBytes":
            suggest = "per_partition_bytes"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in RetentionConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        RetentionConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        RetentionConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 per_partition_bytes: str,
                 period: str):
        """
        The settings for a topic's message retention.
        :param str per_partition_bytes: The provisioned storage, in bytes, per partition. If the number of bytes stored in any of the topic's partitions grows beyond this value, older messages will be dropped to make room for newer ones, regardless of the value of `period`.
        :param str period: How long a published message is retained. If unset, messages will be retained as long as the bytes retained for each partition is below `per_partition_bytes`.
        """
        pulumi.set(__self__, "per_partition_bytes", per_partition_bytes)
        pulumi.set(__self__, "period", period)

    @property
    @pulumi.getter(name="perPartitionBytes")
    def per_partition_bytes(self) -> str:
        """
        The provisioned storage, in bytes, per partition. If the number of bytes stored in any of the topic's partitions grows beyond this value, older messages will be dropped to make room for newer ones, regardless of the value of `period`.
        """
        return pulumi.get(self, "per_partition_bytes")

    @property
    @pulumi.getter
    def period(self) -> str:
        """
        How long a published message is retained. If unset, messages will be retained as long as the bytes retained for each partition is below `per_partition_bytes`.
        """
        return pulumi.get(self, "period")


