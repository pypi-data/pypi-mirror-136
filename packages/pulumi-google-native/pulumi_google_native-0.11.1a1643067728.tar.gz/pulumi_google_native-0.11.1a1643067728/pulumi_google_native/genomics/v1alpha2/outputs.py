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
    'DiskResponse',
    'DockerExecutorResponse',
    'LocalCopyResponse',
    'PipelineParameterResponse',
    'PipelineResourcesResponse',
]

@pulumi.output_type
class DiskResponse(dict):
    """
    A Google Compute Engine disk resource specification.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "mountPoint":
            suggest = "mount_point"
        elif key == "readOnly":
            suggest = "read_only"
        elif key == "sizeGb":
            suggest = "size_gb"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DiskResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DiskResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DiskResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 mount_point: str,
                 name: str,
                 read_only: bool,
                 size_gb: int,
                 source: str,
                 type: str):
        """
        A Google Compute Engine disk resource specification.
        :param str mount_point: Required at create time and cannot be overridden at run time. Specifies the path in the docker container where files on this disk should be located. For example, if `mountPoint` is `/mnt/disk`, and the parameter has `localPath` `inputs/file.txt`, the docker container can access the data at `/mnt/disk/inputs/file.txt`.
        :param str name: The name of the disk that can be used in the pipeline parameters. Must be 1 - 63 characters. The name "boot" is reserved for system use.
        :param bool read_only: Specifies how a sourced-base persistent disk will be mounted. See https://cloud.google.com/compute/docs/disks/persistent-disks#use_multi_instances for more details. Can only be set at create time.
        :param int size_gb: The size of the disk. Defaults to 500 (GB). This field is not applicable for local SSD.
        :param str source: The full or partial URL of the persistent disk to attach. See https://cloud.google.com/compute/docs/reference/latest/instances#resource and https://cloud.google.com/compute/docs/disks/persistent-disks#snapshots for more details.
        :param str type: The type of the disk to create.
        """
        pulumi.set(__self__, "mount_point", mount_point)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "read_only", read_only)
        pulumi.set(__self__, "size_gb", size_gb)
        pulumi.set(__self__, "source", source)
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="mountPoint")
    def mount_point(self) -> str:
        """
        Required at create time and cannot be overridden at run time. Specifies the path in the docker container where files on this disk should be located. For example, if `mountPoint` is `/mnt/disk`, and the parameter has `localPath` `inputs/file.txt`, the docker container can access the data at `/mnt/disk/inputs/file.txt`.
        """
        return pulumi.get(self, "mount_point")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the disk that can be used in the pipeline parameters. Must be 1 - 63 characters. The name "boot" is reserved for system use.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="readOnly")
    def read_only(self) -> bool:
        """
        Specifies how a sourced-base persistent disk will be mounted. See https://cloud.google.com/compute/docs/disks/persistent-disks#use_multi_instances for more details. Can only be set at create time.
        """
        return pulumi.get(self, "read_only")

    @property
    @pulumi.getter(name="sizeGb")
    def size_gb(self) -> int:
        """
        The size of the disk. Defaults to 500 (GB). This field is not applicable for local SSD.
        """
        return pulumi.get(self, "size_gb")

    @property
    @pulumi.getter
    def source(self) -> str:
        """
        The full or partial URL of the persistent disk to attach. See https://cloud.google.com/compute/docs/reference/latest/instances#resource and https://cloud.google.com/compute/docs/disks/persistent-disks#snapshots for more details.
        """
        return pulumi.get(self, "source")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of the disk to create.
        """
        return pulumi.get(self, "type")


@pulumi.output_type
class DockerExecutorResponse(dict):
    """
    The Docker execuctor specification.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "imageName":
            suggest = "image_name"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DockerExecutorResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DockerExecutorResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DockerExecutorResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 cmd: str,
                 image_name: str):
        """
        The Docker execuctor specification.
        :param str cmd: The command or newline delimited script to run. The command string will be executed within a bash shell. If the command exits with a non-zero exit code, output parameter de-localization will be skipped and the pipeline operation's `error` field will be populated. Maximum command string length is 16384.
        :param str image_name: Image name from either Docker Hub or Google Container Registry. Users that run pipelines must have READ access to the image.
        """
        pulumi.set(__self__, "cmd", cmd)
        pulumi.set(__self__, "image_name", image_name)

    @property
    @pulumi.getter
    def cmd(self) -> str:
        """
        The command or newline delimited script to run. The command string will be executed within a bash shell. If the command exits with a non-zero exit code, output parameter de-localization will be skipped and the pipeline operation's `error` field will be populated. Maximum command string length is 16384.
        """
        return pulumi.get(self, "cmd")

    @property
    @pulumi.getter(name="imageName")
    def image_name(self) -> str:
        """
        Image name from either Docker Hub or Google Container Registry. Users that run pipelines must have READ access to the image.
        """
        return pulumi.get(self, "image_name")


@pulumi.output_type
class LocalCopyResponse(dict):
    """
    LocalCopy defines how a remote file should be copied to and from the VM.
    """
    def __init__(__self__, *,
                 disk: str,
                 path: str):
        """
        LocalCopy defines how a remote file should be copied to and from the VM.
        :param str disk: The name of the disk where this parameter is located. Can be the name of one of the disks specified in the Resources field, or "boot", which represents the Docker instance's boot disk and has a mount point of `/`.
        :param str path: The path within the user's docker container where this input should be localized to and from, relative to the specified disk's mount point. For example: file.txt,
        """
        pulumi.set(__self__, "disk", disk)
        pulumi.set(__self__, "path", path)

    @property
    @pulumi.getter
    def disk(self) -> str:
        """
        The name of the disk where this parameter is located. Can be the name of one of the disks specified in the Resources field, or "boot", which represents the Docker instance's boot disk and has a mount point of `/`.
        """
        return pulumi.get(self, "disk")

    @property
    @pulumi.getter
    def path(self) -> str:
        """
        The path within the user's docker container where this input should be localized to and from, relative to the specified disk's mount point. For example: file.txt,
        """
        return pulumi.get(self, "path")


@pulumi.output_type
class PipelineParameterResponse(dict):
    """
    Parameters facilitate setting and delivering data into the pipeline's execution environment. They are defined at create time, with optional defaults, and can be overridden at run time. If `localCopy` is unset, then the parameter specifies a string that is passed as-is into the pipeline, as the value of the environment variable with the given name. A default value can be optionally specified at create time. The default can be overridden at run time using the inputs map. If no default is given, a value must be supplied at runtime. If `localCopy` is defined, then the parameter specifies a data source or sink, both in Google Cloud Storage and on the Docker container where the pipeline computation is run. The service account associated with the Pipeline (by default the project's Compute Engine service account) must have access to the Google Cloud Storage paths. At run time, the Google Cloud Storage paths can be overridden if a default was provided at create time, or must be set otherwise. The pipeline runner should add a key/value pair to either the inputs or outputs map. The indicated data copies will be carried out before/after pipeline execution, just as if the corresponding arguments were provided to `gsutil cp`. For example: Given the following `PipelineParameter`, specified in the `inputParameters` list: ``` {name: "input_file", localCopy: {path: "file.txt", disk: "pd1"}} ``` where `disk` is defined in the `PipelineResources` object as: ``` {name: "pd1", mountPoint: "/mnt/disk/"} ``` We create a disk named `pd1`, mount it on the host VM, and map `/mnt/pd1` to `/mnt/disk` in the docker container. At runtime, an entry for `input_file` would be required in the inputs map, such as: ``` inputs["input_file"] = "gs://my-bucket/bar.txt" ``` This would generate the following gsutil call: ``` gsutil cp gs://my-bucket/bar.txt /mnt/pd1/file.txt ``` The file `/mnt/pd1/file.txt` maps to `/mnt/disk/file.txt` in the Docker container. Acceptable paths are: Google Cloud storage pathLocal path file file glob directory For outputs, the direction of the copy is reversed: ``` gsutil cp /mnt/disk/file.txt gs://my-bucket/bar.txt ``` Acceptable paths are: Local pathGoogle Cloud Storage path file file file directory - directory must already exist glob directory - directory will be created if it doesn't exist One restriction due to docker limitations, is that for outputs that are found on the boot disk, the local path cannot be a glob and must be a file.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "defaultValue":
            suggest = "default_value"
        elif key == "localCopy":
            suggest = "local_copy"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PipelineParameterResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PipelineParameterResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PipelineParameterResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 default_value: str,
                 description: str,
                 local_copy: 'outputs.LocalCopyResponse',
                 name: str):
        """
        Parameters facilitate setting and delivering data into the pipeline's execution environment. They are defined at create time, with optional defaults, and can be overridden at run time. If `localCopy` is unset, then the parameter specifies a string that is passed as-is into the pipeline, as the value of the environment variable with the given name. A default value can be optionally specified at create time. The default can be overridden at run time using the inputs map. If no default is given, a value must be supplied at runtime. If `localCopy` is defined, then the parameter specifies a data source or sink, both in Google Cloud Storage and on the Docker container where the pipeline computation is run. The service account associated with the Pipeline (by default the project's Compute Engine service account) must have access to the Google Cloud Storage paths. At run time, the Google Cloud Storage paths can be overridden if a default was provided at create time, or must be set otherwise. The pipeline runner should add a key/value pair to either the inputs or outputs map. The indicated data copies will be carried out before/after pipeline execution, just as if the corresponding arguments were provided to `gsutil cp`. For example: Given the following `PipelineParameter`, specified in the `inputParameters` list: ``` {name: "input_file", localCopy: {path: "file.txt", disk: "pd1"}} ``` where `disk` is defined in the `PipelineResources` object as: ``` {name: "pd1", mountPoint: "/mnt/disk/"} ``` We create a disk named `pd1`, mount it on the host VM, and map `/mnt/pd1` to `/mnt/disk` in the docker container. At runtime, an entry for `input_file` would be required in the inputs map, such as: ``` inputs["input_file"] = "gs://my-bucket/bar.txt" ``` This would generate the following gsutil call: ``` gsutil cp gs://my-bucket/bar.txt /mnt/pd1/file.txt ``` The file `/mnt/pd1/file.txt` maps to `/mnt/disk/file.txt` in the Docker container. Acceptable paths are: Google Cloud storage pathLocal path file file glob directory For outputs, the direction of the copy is reversed: ``` gsutil cp /mnt/disk/file.txt gs://my-bucket/bar.txt ``` Acceptable paths are: Local pathGoogle Cloud Storage path file file file directory - directory must already exist glob directory - directory will be created if it doesn't exist One restriction due to docker limitations, is that for outputs that are found on the boot disk, the local path cannot be a glob and must be a file.
        :param str default_value: The default value for this parameter. Can be overridden at runtime. If `localCopy` is present, then this must be a Google Cloud Storage path beginning with `gs://`.
        :param str description: Human-readable description.
        :param 'LocalCopyResponse' local_copy: If present, this parameter is marked for copying to and from the VM. `LocalCopy` indicates where on the VM the file should be. The value given to this parameter (either at runtime or using `defaultValue`) must be the remote path where the file should be.
        :param str name: Name of the parameter - the pipeline runner uses this string as the key to the input and output maps in RunPipeline.
        """
        pulumi.set(__self__, "default_value", default_value)
        pulumi.set(__self__, "description", description)
        pulumi.set(__self__, "local_copy", local_copy)
        pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="defaultValue")
    def default_value(self) -> str:
        """
        The default value for this parameter. Can be overridden at runtime. If `localCopy` is present, then this must be a Google Cloud Storage path beginning with `gs://`.
        """
        return pulumi.get(self, "default_value")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Human-readable description.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="localCopy")
    def local_copy(self) -> 'outputs.LocalCopyResponse':
        """
        If present, this parameter is marked for copying to and from the VM. `LocalCopy` indicates where on the VM the file should be. The value given to this parameter (either at runtime or using `defaultValue`) must be the remote path where the file should be.
        """
        return pulumi.get(self, "local_copy")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the parameter - the pipeline runner uses this string as the key to the input and output maps in RunPipeline.
        """
        return pulumi.get(self, "name")


@pulumi.output_type
class PipelineResourcesResponse(dict):
    """
    The system resources for the pipeline run.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "acceleratorCount":
            suggest = "accelerator_count"
        elif key == "acceleratorType":
            suggest = "accelerator_type"
        elif key == "bootDiskSizeGb":
            suggest = "boot_disk_size_gb"
        elif key == "minimumCpuCores":
            suggest = "minimum_cpu_cores"
        elif key == "minimumRamGb":
            suggest = "minimum_ram_gb"
        elif key == "noAddress":
            suggest = "no_address"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PipelineResourcesResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PipelineResourcesResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PipelineResourcesResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 accelerator_count: str,
                 accelerator_type: str,
                 boot_disk_size_gb: int,
                 disks: Sequence['outputs.DiskResponse'],
                 minimum_cpu_cores: int,
                 minimum_ram_gb: float,
                 no_address: bool,
                 preemptible: bool,
                 zones: Sequence[str]):
        """
        The system resources for the pipeline run.
        :param str accelerator_count: Optional. The number of accelerators of the specified type to attach. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit.
        :param str accelerator_type: Optional. The Compute Engine defined accelerator type. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit. Please see https://cloud.google.com/compute/docs/gpus/ for a list of available accelerator types.
        :param int boot_disk_size_gb: The size of the boot disk. Defaults to 10 (GB).
        :param Sequence['DiskResponse'] disks: Disks to attach.
        :param int minimum_cpu_cores: The minimum number of cores to use. Defaults to 1.
        :param float minimum_ram_gb: The minimum amount of RAM to use. Defaults to 3.75 (GB)
        :param bool no_address: Whether to assign an external IP to the instance. This is an experimental feature that may go away. Defaults to false. Corresponds to `--no_address` flag for [gcloud compute instances create] (https://cloud.google.com/sdk/gcloud/reference/compute/instances/create). In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time. If you need to ssh into a private IP VM for debugging, you can ssh to a public VM and then ssh into the private VM's Internal IP. If noAddress is set, this pipeline run may only load docker images from Google Container Registry and not Docker Hub. Before using this, you must [configure access to Google services from internal IPs](https://cloud.google.com/compute/docs/configure-private-google-access#configuring_access_to_google_services_from_internal_ips).
        :param bool preemptible: Whether to use preemptible VMs. Defaults to `false`. In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time.
        :param Sequence[str] zones: List of Google Compute Engine availability zones to which resource creation will restricted. If empty, any zone may be chosen.
        """
        pulumi.set(__self__, "accelerator_count", accelerator_count)
        pulumi.set(__self__, "accelerator_type", accelerator_type)
        pulumi.set(__self__, "boot_disk_size_gb", boot_disk_size_gb)
        pulumi.set(__self__, "disks", disks)
        pulumi.set(__self__, "minimum_cpu_cores", minimum_cpu_cores)
        pulumi.set(__self__, "minimum_ram_gb", minimum_ram_gb)
        pulumi.set(__self__, "no_address", no_address)
        pulumi.set(__self__, "preemptible", preemptible)
        pulumi.set(__self__, "zones", zones)

    @property
    @pulumi.getter(name="acceleratorCount")
    def accelerator_count(self) -> str:
        """
        Optional. The number of accelerators of the specified type to attach. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit.
        """
        return pulumi.get(self, "accelerator_count")

    @property
    @pulumi.getter(name="acceleratorType")
    def accelerator_type(self) -> str:
        """
        Optional. The Compute Engine defined accelerator type. By specifying this parameter, you will download and install the following third-party software onto your managed Compute Engine instances: NVIDIA® Tesla® drivers and NVIDIA® CUDA toolkit. Please see https://cloud.google.com/compute/docs/gpus/ for a list of available accelerator types.
        """
        return pulumi.get(self, "accelerator_type")

    @property
    @pulumi.getter(name="bootDiskSizeGb")
    def boot_disk_size_gb(self) -> int:
        """
        The size of the boot disk. Defaults to 10 (GB).
        """
        return pulumi.get(self, "boot_disk_size_gb")

    @property
    @pulumi.getter
    def disks(self) -> Sequence['outputs.DiskResponse']:
        """
        Disks to attach.
        """
        return pulumi.get(self, "disks")

    @property
    @pulumi.getter(name="minimumCpuCores")
    def minimum_cpu_cores(self) -> int:
        """
        The minimum number of cores to use. Defaults to 1.
        """
        return pulumi.get(self, "minimum_cpu_cores")

    @property
    @pulumi.getter(name="minimumRamGb")
    def minimum_ram_gb(self) -> float:
        """
        The minimum amount of RAM to use. Defaults to 3.75 (GB)
        """
        return pulumi.get(self, "minimum_ram_gb")

    @property
    @pulumi.getter(name="noAddress")
    def no_address(self) -> bool:
        """
        Whether to assign an external IP to the instance. This is an experimental feature that may go away. Defaults to false. Corresponds to `--no_address` flag for [gcloud compute instances create] (https://cloud.google.com/sdk/gcloud/reference/compute/instances/create). In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time. If you need to ssh into a private IP VM for debugging, you can ssh to a public VM and then ssh into the private VM's Internal IP. If noAddress is set, this pipeline run may only load docker images from Google Container Registry and not Docker Hub. Before using this, you must [configure access to Google services from internal IPs](https://cloud.google.com/compute/docs/configure-private-google-access#configuring_access_to_google_services_from_internal_ips).
        """
        return pulumi.get(self, "no_address")

    @property
    @pulumi.getter
    def preemptible(self) -> bool:
        """
        Whether to use preemptible VMs. Defaults to `false`. In order to use this, must be true for both create time and run time. Cannot be true at run time if false at create time.
        """
        return pulumi.get(self, "preemptible")

    @property
    @pulumi.getter
    def zones(self) -> Sequence[str]:
        """
        List of Google Compute Engine availability zones to which resource creation will restricted. If empty, any zone may be chosen.
        """
        return pulumi.get(self, "zones")


