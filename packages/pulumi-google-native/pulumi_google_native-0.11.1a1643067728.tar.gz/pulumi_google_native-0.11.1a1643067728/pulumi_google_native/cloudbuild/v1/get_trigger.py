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
    'GetTriggerResult',
    'AwaitableGetTriggerResult',
    'get_trigger',
    'get_trigger_output',
]

@pulumi.output_type
class GetTriggerResult:
    def __init__(__self__, approval_config=None, autodetect=None, bitbucket_server_trigger_config=None, build=None, create_time=None, description=None, disabled=None, event_type=None, filename=None, filter=None, git_file_source=None, github=None, ignored_files=None, included_files=None, name=None, pubsub_config=None, resource_name=None, service_account=None, source_to_build=None, substitutions=None, tags=None, trigger_template=None, webhook_config=None):
        if approval_config and not isinstance(approval_config, dict):
            raise TypeError("Expected argument 'approval_config' to be a dict")
        pulumi.set(__self__, "approval_config", approval_config)
        if autodetect and not isinstance(autodetect, bool):
            raise TypeError("Expected argument 'autodetect' to be a bool")
        pulumi.set(__self__, "autodetect", autodetect)
        if bitbucket_server_trigger_config and not isinstance(bitbucket_server_trigger_config, dict):
            raise TypeError("Expected argument 'bitbucket_server_trigger_config' to be a dict")
        pulumi.set(__self__, "bitbucket_server_trigger_config", bitbucket_server_trigger_config)
        if build and not isinstance(build, dict):
            raise TypeError("Expected argument 'build' to be a dict")
        pulumi.set(__self__, "build", build)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if disabled and not isinstance(disabled, bool):
            raise TypeError("Expected argument 'disabled' to be a bool")
        pulumi.set(__self__, "disabled", disabled)
        if event_type and not isinstance(event_type, str):
            raise TypeError("Expected argument 'event_type' to be a str")
        pulumi.set(__self__, "event_type", event_type)
        if filename and not isinstance(filename, str):
            raise TypeError("Expected argument 'filename' to be a str")
        pulumi.set(__self__, "filename", filename)
        if filter and not isinstance(filter, str):
            raise TypeError("Expected argument 'filter' to be a str")
        pulumi.set(__self__, "filter", filter)
        if git_file_source and not isinstance(git_file_source, dict):
            raise TypeError("Expected argument 'git_file_source' to be a dict")
        pulumi.set(__self__, "git_file_source", git_file_source)
        if github and not isinstance(github, dict):
            raise TypeError("Expected argument 'github' to be a dict")
        pulumi.set(__self__, "github", github)
        if ignored_files and not isinstance(ignored_files, list):
            raise TypeError("Expected argument 'ignored_files' to be a list")
        pulumi.set(__self__, "ignored_files", ignored_files)
        if included_files and not isinstance(included_files, list):
            raise TypeError("Expected argument 'included_files' to be a list")
        pulumi.set(__self__, "included_files", included_files)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if pubsub_config and not isinstance(pubsub_config, dict):
            raise TypeError("Expected argument 'pubsub_config' to be a dict")
        pulumi.set(__self__, "pubsub_config", pubsub_config)
        if resource_name and not isinstance(resource_name, str):
            raise TypeError("Expected argument 'resource_name' to be a str")
        pulumi.set(__self__, "resource_name", resource_name)
        if service_account and not isinstance(service_account, str):
            raise TypeError("Expected argument 'service_account' to be a str")
        pulumi.set(__self__, "service_account", service_account)
        if source_to_build and not isinstance(source_to_build, dict):
            raise TypeError("Expected argument 'source_to_build' to be a dict")
        pulumi.set(__self__, "source_to_build", source_to_build)
        if substitutions and not isinstance(substitutions, dict):
            raise TypeError("Expected argument 'substitutions' to be a dict")
        pulumi.set(__self__, "substitutions", substitutions)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)
        if trigger_template and not isinstance(trigger_template, dict):
            raise TypeError("Expected argument 'trigger_template' to be a dict")
        pulumi.set(__self__, "trigger_template", trigger_template)
        if webhook_config and not isinstance(webhook_config, dict):
            raise TypeError("Expected argument 'webhook_config' to be a dict")
        pulumi.set(__self__, "webhook_config", webhook_config)

    @property
    @pulumi.getter(name="approvalConfig")
    def approval_config(self) -> 'outputs.ApprovalConfigResponse':
        """
        Configuration for manual approval to start a build invocation of this BuildTrigger.
        """
        return pulumi.get(self, "approval_config")

    @property
    @pulumi.getter
    def autodetect(self) -> bool:
        """
        Autodetect build configuration. The following precedence is used (case insensitive): 1. cloudbuild.yaml 2. cloudbuild.yml 3. cloudbuild.json 4. Dockerfile Currently only available for GitHub App Triggers.
        """
        return pulumi.get(self, "autodetect")

    @property
    @pulumi.getter(name="bitbucketServerTriggerConfig")
    def bitbucket_server_trigger_config(self) -> 'outputs.BitbucketServerTriggerConfigResponse':
        """
        BitbucketServerTriggerConfig describes the configuration of a trigger that creates a build whenever a Bitbucket Server event is received.
        """
        return pulumi.get(self, "bitbucket_server_trigger_config")

    @property
    @pulumi.getter
    def build(self) -> 'outputs.BuildResponse':
        """
        Contents of the build template.
        """
        return pulumi.get(self, "build")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        Time when the trigger was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Human-readable description of this trigger.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def disabled(self) -> bool:
        """
        If true, the trigger will never automatically execute a build.
        """
        return pulumi.get(self, "disabled")

    @property
    @pulumi.getter(name="eventType")
    def event_type(self) -> str:
        """
        EventType allows the user to explicitly set the type of event to which this BuildTrigger should respond. This field will be validated against the rest of the configuration if it is set.
        """
        return pulumi.get(self, "event_type")

    @property
    @pulumi.getter
    def filename(self) -> str:
        """
        Path, from the source root, to the build configuration file (i.e. cloudbuild.yaml).
        """
        return pulumi.get(self, "filename")

    @property
    @pulumi.getter
    def filter(self) -> str:
        """
        A Common Expression Language string.
        """
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter(name="gitFileSource")
    def git_file_source(self) -> 'outputs.GitFileSourceResponse':
        """
        The file source describing the local or remote Build template.
        """
        return pulumi.get(self, "git_file_source")

    @property
    @pulumi.getter
    def github(self) -> 'outputs.GitHubEventsConfigResponse':
        """
        GitHubEventsConfig describes the configuration of a trigger that creates a build whenever a GitHub event is received. Mutually exclusive with `trigger_template`.
        """
        return pulumi.get(self, "github")

    @property
    @pulumi.getter(name="ignoredFiles")
    def ignored_files(self) -> Sequence[str]:
        """
        ignored_files and included_files are file glob matches using https://golang.org/pkg/path/filepath/#Match extended with support for "**". If ignored_files and changed files are both empty, then they are not used to determine whether or not to trigger a build. If ignored_files is not empty, then we ignore any files that match any of the ignored_file globs. If the change has no files that are outside of the ignored_files globs, then we do not trigger a build.
        """
        return pulumi.get(self, "ignored_files")

    @property
    @pulumi.getter(name="includedFiles")
    def included_files(self) -> Sequence[str]:
        """
        If any of the files altered in the commit pass the ignored_files filter and included_files is empty, then as far as this filter is concerned, we should trigger the build. If any of the files altered in the commit pass the ignored_files filter and included_files is not empty, then we make sure that at least one of those files matches a included_files glob. If not, then we do not trigger a build.
        """
        return pulumi.get(self, "included_files")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        User-assigned name of the trigger. Must be unique within the project. Trigger names must meet the following requirements: + They must contain only alphanumeric characters and dashes. + They can be 1-64 characters long. + They must begin and end with an alphanumeric character.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="pubsubConfig")
    def pubsub_config(self) -> 'outputs.PubsubConfigResponse':
        """
        PubsubConfig describes the configuration of a trigger that creates a build whenever a Pub/Sub message is published.
        """
        return pulumi.get(self, "pubsub_config")

    @property
    @pulumi.getter(name="resourceName")
    def resource_name(self) -> str:
        """
        The `Trigger` name with format: `projects/{project}/locations/{location}/triggers/{trigger}`, where {trigger} is a unique identifier generated by the service.
        """
        return pulumi.get(self, "resource_name")

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> str:
        """
        The service account used for all user-controlled operations including UpdateBuildTrigger, RunBuildTrigger, CreateBuild, and CancelBuild. If no service account is set, then the standard Cloud Build service account ([PROJECT_NUM]@system.gserviceaccount.com) will be used instead. Format: `projects/{PROJECT_ID}/serviceAccounts/{ACCOUNT_ID_OR_EMAIL}`
        """
        return pulumi.get(self, "service_account")

    @property
    @pulumi.getter(name="sourceToBuild")
    def source_to_build(self) -> 'outputs.GitRepoSourceResponse':
        """
        The repo and ref of the repository from which to build. This field is used only for those triggers that do not respond to SCM events. Triggers that respond to such events build source at whatever commit caused the event. This field is currently only used by Webhook, Pub/Sub, Manual, and Cron triggers.
        """
        return pulumi.get(self, "source_to_build")

    @property
    @pulumi.getter
    def substitutions(self) -> Mapping[str, str]:
        """
        Substitutions for Build resource. The keys must match the following regular expression: `^_[A-Z0-9_]+$`.
        """
        return pulumi.get(self, "substitutions")

    @property
    @pulumi.getter
    def tags(self) -> Sequence[str]:
        """
        Tags for annotation of a `BuildTrigger`
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="triggerTemplate")
    def trigger_template(self) -> 'outputs.RepoSourceResponse':
        """
        Template describing the types of source changes to trigger a build. Branch and tag names in trigger templates are interpreted as regular expressions. Any branch or tag change that matches that regular expression will trigger a build. Mutually exclusive with `github`.
        """
        return pulumi.get(self, "trigger_template")

    @property
    @pulumi.getter(name="webhookConfig")
    def webhook_config(self) -> 'outputs.WebhookConfigResponse':
        """
        WebhookConfig describes the configuration of a trigger that creates a build whenever a webhook is sent to a trigger's webhook URL.
        """
        return pulumi.get(self, "webhook_config")


class AwaitableGetTriggerResult(GetTriggerResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetTriggerResult(
            approval_config=self.approval_config,
            autodetect=self.autodetect,
            bitbucket_server_trigger_config=self.bitbucket_server_trigger_config,
            build=self.build,
            create_time=self.create_time,
            description=self.description,
            disabled=self.disabled,
            event_type=self.event_type,
            filename=self.filename,
            filter=self.filter,
            git_file_source=self.git_file_source,
            github=self.github,
            ignored_files=self.ignored_files,
            included_files=self.included_files,
            name=self.name,
            pubsub_config=self.pubsub_config,
            resource_name=self.resource_name,
            service_account=self.service_account,
            source_to_build=self.source_to_build,
            substitutions=self.substitutions,
            tags=self.tags,
            trigger_template=self.trigger_template,
            webhook_config=self.webhook_config)


def get_trigger(location: Optional[str] = None,
                project: Optional[str] = None,
                project_id: Optional[str] = None,
                trigger_id: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetTriggerResult:
    """
    Returns information about a `BuildTrigger`. This API is experimental.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['project'] = project
    __args__['projectId'] = project_id
    __args__['triggerId'] = trigger_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('google-native:cloudbuild/v1:getTrigger', __args__, opts=opts, typ=GetTriggerResult).value

    return AwaitableGetTriggerResult(
        approval_config=__ret__.approval_config,
        autodetect=__ret__.autodetect,
        bitbucket_server_trigger_config=__ret__.bitbucket_server_trigger_config,
        build=__ret__.build,
        create_time=__ret__.create_time,
        description=__ret__.description,
        disabled=__ret__.disabled,
        event_type=__ret__.event_type,
        filename=__ret__.filename,
        filter=__ret__.filter,
        git_file_source=__ret__.git_file_source,
        github=__ret__.github,
        ignored_files=__ret__.ignored_files,
        included_files=__ret__.included_files,
        name=__ret__.name,
        pubsub_config=__ret__.pubsub_config,
        resource_name=__ret__.resource_name,
        service_account=__ret__.service_account,
        source_to_build=__ret__.source_to_build,
        substitutions=__ret__.substitutions,
        tags=__ret__.tags,
        trigger_template=__ret__.trigger_template,
        webhook_config=__ret__.webhook_config)


@_utilities.lift_output_func(get_trigger)
def get_trigger_output(location: Optional[pulumi.Input[str]] = None,
                       project: Optional[pulumi.Input[Optional[str]]] = None,
                       project_id: Optional[pulumi.Input[str]] = None,
                       trigger_id: Optional[pulumi.Input[str]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetTriggerResult]:
    """
    Returns information about a `BuildTrigger`. This API is experimental.
    """
    ...
