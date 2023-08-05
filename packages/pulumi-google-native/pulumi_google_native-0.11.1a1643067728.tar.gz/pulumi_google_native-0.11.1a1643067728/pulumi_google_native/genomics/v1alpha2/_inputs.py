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
    'DiskArgs',
    'DockerExecutorArgs',
    'LocalCopyArgs',
    'PipelineParameterArgs',
    'PipelineResourcesArgs',
]

@pulumi.input_type
class DiskArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 type: pulumi.Input['DiskType'],
                 mount_point: Optional[pulumi.Input[str]] = None,
                 read_only: Optional[pulumi.Input[bool]] = None,
                 size_gb: Optional[pulumi.Input[int]] = None,
                 source: Optional[pulumi.Input[str]] = None):
        """
        A Google Compute Engine disk resource specification.
        :param pulumi.Input[str] name: The name of the disk that can be used in the pipeline parameters. Must be 1 - 63 characters. The name "boot" is reserved for system use.
        :param pulumi.Input['DiskType'] type: The type of the disk to create.
        :param pulumi.Input[str] mount_point: Required at create time and cannot be overridden at run time. Specifies the path in the docker container where files on this disk should be located. For example, if `mountPoint` is `/mnt/disk`, and the parameter has `localPath` `inputs/file.txt`, the docker container can access the data at `/mnt/disk/inputs/file.txt`.
        :param pulumi.Input[bool] read_only: Specifies how a sourced-base persistent disk will be mounted. See https://cloud.google.com/compute/docs/disks/persistent-disks#use_multi_instances for more details. Can only be set at create time.
        :param pulumi.Input[int] size_gb: The size of the disk. Defaults to 500 (GB). This field is not applicable for local SSD.
        :param pulumi.Input[str] source: The full or partial URL of the persistent disk to attach. See https://cloud.google.com/compute/docs/reference/latest/instances#resource and https://cloud.google.com/compute/docs/disks/persistent-disks#snapshots for more details.
        """
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "type", type)
        if mount_point is not None:
            pulumi.set(__self__, "mount_point", mount_point)
        if read_only is not None:
            pulumi.set(__self__, "read_only", read_only)
        if size_gb is not None:
            pulumi.set(__self__, "size_gb", size_gb)
        if source is not None:
            pulumi.set(__self__, "source", source)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        The name of the disk that can be used in the pipeline parameters. Must be 1 - 63 characters. The name "boot" is reserved for system use.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input['DiskType']:
        """
        The type of the disk to create.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input['DiskType']):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter(name="mountPoint")
    def mount_point(self) -> Optional[pulumi.Input[str]]:
        """
        Required at create time and cannot be overridden at run time. Specifies the path in the docker container where files on this disk should be located. For example, if `mountPoint` is `/mnt/disk`, and the parameter has `localPath` `inputs/file.txt`, the docker container can access the data at `/mnt/disk/inputs/file.txt`.
        """
        return pulumi.get(self, "mount_point")

    @mount_point.setter
    def mount_point(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "mount_point", value)

    @property
    @pulumi.getter(name="readOnly")
    def read_only(self) -> Optional[pulumi.Input[bool]]:
        """
        Specifies how a sourced-base persistent disk will be mounted. See https://cloud.google.com/compute/docs/disks/persistent-disks#use_multi_instances for more details. Can only be set at create time.
        """
        return pulumi.get(self, "read_only")

    @read_only.setter
    def read_only(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "read_only", value)

    @property
    @pulumi.getter(name="sizeGb")
    def size_gb(self) -> Optional[pulumi.Input[int]]:
        """
        The size of the disk. Defaults to 500 (GB). This field is not applicable for local SSD.
        """
        return pulumi.get(self, "size_gb")

    @size_gb.setter
    def size_gb(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "size_gb", value)

    @property
    @pulumi.getter
    def source(self) -> Optional[pulumi.Input[str]]:
        """
        The full or partial URL of the persistent disk to attach. See https://cloud.google.com/compute/docs/reference/latest/instances#resource and https://cloud.google.com/compute/docs/disks/persistent-disks#snapshots for more details.
        """
        return pulumi.get(self, "source")

    @source.setter
    def source(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "source", value)


@pulumi.input_type
class DockerExecutorArgs:
    def __init__(__self__, *,
                 cmd: pulumi.Input[str],
                 image_name: pulumi.Input[str]):
        """
        The Docker execuctor specification.
        :param pulumi.Input[str] cmd: The command or newline delimited script to run. The command string will be executed within a bash shell. If the command exits with a non-zero exit code, output parameter de-localization will be skipped and the pipeline operation's `error` field will be populated. Maximum command string length is 16384.
        :param pulumi.Input[str] image_name: Image name from either Docker Hub or Google Container Registry. Users that run pipelines must have READ access to the image.
        """
        pulumi.set(__self__, "cmd", cmd)
        pulumi.set(__self__, "image_name", image_name)

    @property
    @pulumi.getter
    def cmd(self) -> pulumi.Input[str]:
        """
        The command or newline delimited script to run. The command string will be executed within a bash shell. If the command exits with a non-zero exit code, output parameter de-localization will be skipped and the pipeline operation's `error` field will be populated. Maximum command string length is 16384.
        """
        return pulumi.get(self, "cmd")

    @cmd.setter
    def cmd(self, value: pulumi.Input[str]):
        pulumi.set(self, "cmd", value)

    @property
    @pulumi.getter(name="imageName")
    def image_name(self) -> pulumi.Input[str]:
        """
        Image name from either Docker Hub or Google Container Registry. Users that run pipelines must have READ access to the image.
        """
        return pulumi.get(self, "image_name")

    @image_name.setter
    def image_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "image_name", value)


@pulumi.input_type
class LocalCopyArgs:
    def __init__(__self__, *,
                 disk: pulumi.Input[str],
                 path: pulumi.Input[str]):
        """
        LocalCopy defines how a remote file should be copied to and from the VM.
        :param pulumi.Input[str] disk: The name of the disk where this parameter is located. Can be the name of one of the disks specified in the Resources field, or "boot", which represents the Docker instance's boot disk and has a mount point of `/`.
        :param pulumi.Input[str] path: The path within the user's docker container where this input should be localized to and from, relative to the specified disk's mount point. For example: file.txt,
        """
        pulumi.set(__self__, "disk", disk)
        pulumi.set(__self__, "path", path)

    @property
    @pulumi.getter
    def disk(self) -> pulumi.Input[str]:
        """
        The name of the disk where this parameter is located. Can be the name of one of the disks specified in the Resources field, or "boot", which represents the Docker instance's boot disk and has a mount point of `/`.
        """
        return pulumi.get(self, "disk")

    @disk.setter
    def disk(self, value: pulumi.Input[str]):
        pulumi.set(self, "disk", value)

    @property
    @pulumi.getter
    def path(self) -> pulumi.Input[str]:
        """
        The path within the user's docker container where this input should be localized to and from, relative to the specified disk's mount point. For example: file.txt,
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: pulumi.Input[str]):
        pulumi.set(self, "path", value)


@pulumi.input_type
class PipelineParameterArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 default_value: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 local_copy: Optional[pulumi.Input['LocalCopyArgs']] = None):
        """
        Parameters facilitate setting and delivering data into the pipeline's execution environment. They are defined at create time, with optional defaults, and can be overridden at run time. If `localCopy` is unset, then the parameter specifies a string that is passed as-is into the pipeline, as the value of the environment variable with the given name. A default value can be optionally specified at create time. The default can be overridden at run time using the inputs map. If no default is given, a value must be supplied at runtime. If `localCopy` is defined, then the parameter specifies a data source or sink, both in Google Cloud Storage and on the Docker container where the pipeline computation is run. The service account associated with the Pipeline (by default the project's Compute Engine service account) must have access to the Google Cloud Storage paths. At run time, the Google Cloud Storage paths can be overridden if a default was provided at create time, or must be set otherwise. The pipeline runner should add a key/value pair to either the inputs or outputs map. The indicated data copies will be carried out before/after pipeline execution, just as if the corresponding arguments were provided to `gsutil cp`. For example: Given the following `PipelineParameter`, specified in the `inputParameters` list: ``` {name: "input_file", localCopy: {path: "file.txt", disk: "pd1"}} ``` where `disk` is defined in the `PipelineResources` object as: ``` {name: "pd1", mountPoint: "/mnt/disk/"} ``` We create a disk named `pd1`, mount it on the host VM, and map `/mnt/pd1` to `/mnt/disk` in the docker container. At runtime, an entry for `input_file` would be required in the inputs map, such as: ``` inputs["input_file"] = "gs://my-bucket/bar.txt" ``` This would generate the following gsutil call: ``` gsutil cp gs://my-bucket/bar.txt /mnt/pd1/file.txt ``` The file `/mnt/pd1/file.txt` maps to `/mnt/disk/file.txt` in the Docker container. Acceptable paths are: Google Cloud storage pathLocal path file file glob directory For outputs, the direction of the copy is reversed: ``` gsutil cp /mnt/disk/file.txt gs://my-bucket/bar.txt ``` Acceptable paths are: Local pathGoogle Cloud Storage path file file file directory - directory must already exist glob directory - directory will be created if it doesn't exist One restriction due to docker limitations, is that for outputs that are found on the boot disk, the local path cannot be a glob and must be a file.
        :param pulumi.Input[str] name: Name of the parameter - the pipeline runner uses this string as the key to the input and output maps in RunPipeline.
        :param pulumi.Input[str] default_value: The default value for this parameter. Can be overridden at runtime. If `localCopy` is present, then this must be a Google Cloud Storage path beginning with `gs://`.
        :param pulumi.Input[str] description: Human-readable description.
        :param pulumi.Input['LocalCopyArgs'] local_copy: If present, this parameter is marked for copying to and from the VM. `LocalCopy` indicates where on the VM the file should be. The value given to this parameter (either at runtime or using `defaultValue`) must be the remote path where the file should be.
        """
        pulumi.set(__self__, "name", name)
        if default_value is not None:
            pulumi.set(__self__, "default_value", default_value)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if local_copy is not None:
            pulumi.set(__self__, "local_copy", local_copy)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        Name of the parameter - the pipeline runner uses this string as the key to the input and output maps in RunPipeline.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="defaultValue")
    def default_value(self) -> Optional[pulumi.Input[str]]:
        """
        The default value for this parameter. Can be overridden at runtime. If `localCopy` is present, then this must be a Google Cloud Storage path beginning with `gs://`.
        """
        return pulumi.get(self, "default_value")

    @default_value.setter
    def default_value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "default_value", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Human-readable description.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="localCopy")
    def local_copy(self) -> Optional[pulumi.Input['LocalCopyArgs']]:
        """
        If present, this parameter is marked for copying to and from the VM. `LocalCopy` indicates where on the VM the file should be. The value given to this parameter (either at runtime or using `defaultValue`) must be the remote path where the file should be.
        """
        return pulumi.get(self, "local_copy")

    @local_copy.setter
    def local_copy(self, value: Optional[pulumi.Input['LocalCopyArgs']]):
        pulumi.set(self, "local_copy", value)


@pulumi.input_type
class PipelineResourcesArgs:
    def __init__(__self__, *,
                 accelerator_count: Optional[pulumi.Input[str]] = None,
                 accelerator_type: Optional[pulumi.Input[str]] = None,
                 boot_disk_size_gb: Optional[pulumi.Input[int]] = None,
                 disks: Optional[pulumi.Input[Sequence[pulumi.Input['DiskArgs']]]] = None,
                 minimum_cpu_cores: Optional[pulumi.Input[int]] = None,
                 minimum_ram_gb: Optional[pulumi.Input[float]] = None,
                 no_address: Optional[pulumi.Input[bool]] = None,
                 preemptible: Optional[pulumi.Input[bool]] = None,
                 zones: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The system resources for the pipeline run.
        :param pulumi.Input[str] accelerator_count: Optional. The number of accelerators of the specified type to attach. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit.
        :param pulumi.Input[str] accelerator_type: Optional. The Compute Engine defined accelerator type. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit. Please see https://cloud.google.com/compute/docs/gpus/ for a list of available accelerator types.
        :param pulumi.Input[int] boot_disk_size_gb: The size of the boot disk. Defaults to 10 (GB).
        :param pulumi.Input[Sequence[pulumi.Input['DiskArgs']]] disks: Disks to attach.
        :param pulumi.Input[int] minimum_cpu_cores: The minimum number of cores to use. Defaults to 1.
        :param pulumi.Input[float] minimum_ram_gb: The minimum amount of RAM to use. Defaults to 3.75 (GB)
        :param pulumi.Input[bool] no_address: Whether to assign an external IP to the instance. This is an experimental feature that may go away. Defaults to false. Corresponds to `--no_address` flag for [gcloud compute instances create] (https://cloud.google.com/sdk/gcloud/reference/compute/instances/create). In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time. If you need to ssh into a private IP VM for debugging, you can ssh to a public VM and then ssh into the private VM's Internal IP. If noAddress is set, this pipeline run may only load docker images from Google Container Registry and not Docker Hub. Before using this, you must [configure access to Google services from internal IPs](https://cloud.google.com/compute/docs/configure-private-google-access#configuring_access_to_google_services_from_internal_ips).
        :param pulumi.Input[bool] preemptible: Whether to use preemptible VMs. Defaults to `false`. In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] zones: List of Google Compute Engine availability zones to which resource creation will restricted. If empty, any zone may be chosen.
        """
        if accelerator_count is not None:
            pulumi.set(__self__, "accelerator_count", accelerator_count)
        if accelerator_type is not None:
            pulumi.set(__self__, "accelerator_type", accelerator_type)
        if boot_disk_size_gb is not None:
            pulumi.set(__self__, "boot_disk_size_gb", boot_disk_size_gb)
        if disks is not None:
            pulumi.set(__self__, "disks", disks)
        if minimum_cpu_cores is not None:
            pulumi.set(__self__, "minimum_cpu_cores", minimum_cpu_cores)
        if minimum_ram_gb is not None:
            pulumi.set(__self__, "minimum_ram_gb", minimum_ram_gb)
        if no_address is not None:
            pulumi.set(__self__, "no_address", no_address)
        if preemptible is not None:
            pulumi.set(__self__, "preemptible", preemptible)
        if zones is not None:
            pulumi.set(__self__, "zones", zones)

    @property
    @pulumi.getter(name="acceleratorCount")
    def accelerator_count(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. The number of accelerators of the specified type to attach. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit.
        """
        return pulumi.get(self, "accelerator_count")

    @accelerator_count.setter
    def accelerator_count(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "accelerator_count", value)

    @property
    @pulumi.getter(name="acceleratorType")
    def accelerator_type(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. The Compute Engine defined accelerator type. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit. Please see https://cloud.google.com/compute/docs/gpus/ for a list of available accelerator types.
        """
        return pulumi.get(self, "accelerator_type")

    @accelerator_type.setter
    def accelerator_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "accelerator_type", value)

    @property
    @pulumi.getter(name="bootDiskSizeGb")
    def boot_disk_size_gb(self) -> Optional[pulumi.Input[int]]:
        """
        The size of the boot disk. Defaults to 10 (GB).
        """
        return pulumi.get(self, "boot_disk_size_gb")

    @boot_disk_size_gb.setter
    def boot_disk_size_gb(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "boot_disk_size_gb", value)

    @property
    @pulumi.getter
    def disks(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['DiskArgs']]]]:
        """
        Disks to attach.
        """
        return pulumi.get(self, "disks")

    @disks.setter
    def disks(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['DiskArgs']]]]):
        pulumi.set(self, "disks", value)

    @property
    @pulumi.getter(name="minimumCpuCores")
    def minimum_cpu_cores(self) -> Optional[pulumi.Input[int]]:
        """
        The minimum number of cores to use. Defaults to 1.
        """
        return pulumi.get(self, "minimum_cpu_cores")

    @minimum_cpu_cores.setter
    def minimum_cpu_cores(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "minimum_cpu_cores", value)

    @property
    @pulumi.getter(name="minimumRamGb")
    def minimum_ram_gb(self) -> Optional[pulumi.Input[float]]:
        """
        The minimum amount of RAM to use. Defaults to 3.75 (GB)
        """
        return pulumi.get(self, "minimum_ram_gb")

    @minimum_ram_gb.setter
    def minimum_ram_gb(self, value: Optional[pulumi.Input[float]]):
        pulumi.set(self, "minimum_ram_gb", value)

    @property
    @pulumi.getter(name="noAddress")
    def no_address(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether to assign an external IP to the instance. This is an experimental feature that may go away. Defaults to false. Corresponds to `--no_address` flag for [gcloud compute instances create] (https://cloud.google.com/sdk/gcloud/reference/compute/instances/create). In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time. If you need to ssh into a private IP VM for debugging, you can ssh to a public VM and then ssh into the private VM's Internal IP. If noAddress is set, this pipeline run may only load docker images from Google Container Registry and not Docker Hub. Before using this, you must [configure access to Google services from internal IPs](https://cloud.google.com/compute/docs/configure-private-google-access#configuring_access_to_google_services_from_internal_ips).
        """
        return pulumi.get(self, "no_address")

    @no_address.setter
    def no_address(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "no_address", value)

    @property
    @pulumi.getter
    def preemptible(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether to use preemptible VMs. Defaults to `false`. In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time.
        """
        return pulumi.get(self, "preemptible")

    @preemptible.setter
    def preemptible(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "preemptible", value)

    @property
    @pulumi.getter
    def zones(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of Google Compute Engine availability zones to which resource creation will restricted. If empty, any zone may be chosen.
        """
        return pulumi.get(self, "zones")

    @zones.setter
    def zones(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "zones", value)


