"""Defines the Pydantic model for a pipeline."""

import io
import typing as t
from datetime import datetime, timezone

import yaml
from pydantic import BaseModel, Field, field_validator


class ExecutionSummaryInfo(BaseModel):
    number_of_errors: t.Annotated[t.List[int], Field(alias="numOfErrors")]
    deployments: t.List[int]
    last_execution_ts: t.Annotated[
        t.Optional[datetime], Field(alias="lastExecutionTs")
    ] = None
    last_execution_status: t.Annotated[
        t.Optional[str], Field(alias="lastExecutionStatus")
    ] = None
    last_execution_id: t.Annotated[t.Optional[str], Field(alias="lastExecutionId")] = (
        None
    )

    @field_validator("last_execution_ts", mode="before")
    @classmethod
    def convert_epoch_to_datetime(cls, ts: t.Any):
        if isinstance(ts, (float, int)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return ts


class GitDetails(BaseModel):
    valid: bool = True
    invalid_yaml: t.Annotated[t.Optional[str], Field(alias="invalidYaml")] = None


class EntityValidityDetails(BaseModel):
    valid: bool = True
    invalid_yaml: t.Annotated[t.Optional[str], Field(alias="invalidYaml")] = None


class PublicAccess(BaseModel):
    public: bool = False
    error_message: t.Annotated[t.Optional[str], Field(alias="errorMessage")] = None


class ExecutionInfo(BaseModel):
    trigger_type: t.Annotated[str, Field(alias="triggerType")]
    username: t.Annotated[str, Field(alias="username")]


class RecentExecutionsInfo(BaseModel):
    plan_execution_id: t.Annotated[str, Field(alias="planExecutionId")]
    status: t.Annotated[str, Field(alias="status")]
    start_ts: t.Annotated[int, Field(alias="startTs")]
    executor_info: t.Annotated[ExecutionInfo, Field(alias="executorInfo")]


class PipelineSummary(BaseModel):
    name: str
    identifier: str
    description: str = ""
    tags: t.Dict[str, str] = {}
    version: int = 0
    number_of_stages: t.Annotated[int, Field(alias="numOfStages")]
    created_at: t.Annotated[datetime, Field(alias="createdAt")]
    last_updated_at: t.Annotated[datetime, Field(alias="lastUpdatedAt")]
    modules: t.List[str]
    execution_summary: t.Annotated[
        ExecutionSummaryInfo, Field(alias="executionSummaryInfo")
    ]
    filters: t.Dict[str, t.Any]
    stage_names: t.Annotated[t.List[str], Field(alias="stageNames")]
    git_details: t.Annotated[t.Optional[GitDetails], Field(alias="gitDetails")] = None
    entity_validity: t.Annotated[
        EntityValidityDetails, Field(alias="entityValidityDetails")
    ]
    store_type: t.Annotated[str, Field(alias="storeType")] = "INLINE"
    connector_ref: t.Annotated[t.Optional[str], Field(alias="connectorRef")] = None
    is_draft: t.Annotated[bool, Field(alias="isDraft")] = False
    yaml_version: t.Annotated[str, Field(alias="yamlVersion")] = "0"

    @field_validator("created_at", "last_updated_at", mode="before")
    @classmethod
    def convert_epoch_to_datetime(cls, ts: t.Any):
        if isinstance(ts, (float, int)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return ts

    recent_executions_info: t.Annotated[
        t.List[RecentExecutionsInfo], Field(alias="recentExecutionsInfo")
    ] = []  # TODO(ankush): 90% sure we are suing a different API than you and this field will be empty?


class Pipeline(BaseModel):
    pipeline_yaml: t.Annotated[str, Field(alias="yamlPipeline")]
    resolved_template_pipeline_yaml: t.Annotated[
        t.Optional[None], Field(alias="resolvedTemplatePipelineYaml")
    ] = None
    git_details: t.Annotated[t.Optional[GitDetails], Field(alias="gitDetails")] = None
    entity_validity: t.Annotated[
        EntityValidityDetails, Field(alias="entityValidityDetails")
    ]
    modules: t.List[str]
    validation_uuid: t.Annotated[t.Optional[str], Field(alias="validationUuid")] = None
    store_type: t.Annotated[str, Field(alias="storeType")] = "INLINE"
    public_access: t.Annotated[
        t.Optional[PublicAccess], Field(alias="publicAccessResponse")
    ] = None

    @property
    def pipeline_dict(self) -> t.Dict[str, t.Any]:
        return yaml.safe_load(io.StringIO(self.pipeline_yaml))

    @property
    def resolved_template_pipeline_dict(self) -> t.Dict[str, t.Any]:
        if self.resolved_template_pipeline_yaml is None:
            return {}
        return yaml.safe_load(io.StringIO(self.resolved_template_pipeline_yaml))


class ExtraInfo(BaseModel):
    execution_trigger_tag_needed_for_abort: t.Optional[str] = None
    trigger_ref: t.Annotated[t.Optional[str], Field(alias="triggerRef")] = None
    event_correlation_id: t.Annotated[
        t.Optional[str], Field(alias="eventCorrelationId")
    ] = None


class TriggeredBy(BaseModel):
    uuid: str
    identifier: str
    extra_info: t.Annotated[ExtraInfo, Field(alias="extraInfo")]
    trigger_identifier: t.Annotated[str, Field(alias="triggerIdentifier")]
    trigger_name: t.Annotated[str, Field(alias="triggerName")]


class ExecutionTriggerInfo(BaseModel):
    trigger_type: t.Annotated[str, Field(alias="triggerType")]
    triggered_by: TriggeredBy = Field(alias="triggeredBy")
    is_rerun: t.Annotated[bool, Field(alias="isRerun")]


class GovernanceMetadata(BaseModel):
    id: str
    deny: bool
    details: t.List[t.Any] = []
    message: str
    timestamp: str
    status: str
    account_id: t.Annotated[str, Field(alias="accountId")]
    org_id: t.Annotated[str, Field(alias="orgId")]
    project_id: t.Annotated[str, Field(alias="projectId")]
    entity: str
    type: str
    action: str
    created: str


class CIImageDetails(BaseModel):
    image_name: t.Annotated[str, Field(alias="imageName")]
    image_tag: t.Annotated[str, Field(alias="imageTag")]


class CIInfraDetails(BaseModel):
    infra_type: t.Annotated[str, Field(alias="infraType")]
    infra_os_type: t.Annotated[str, Field(alias="infraOSType")]
    infra_host_type: t.Annotated[str, Field(alias="infraHostType")]
    infra_arch_type: t.Annotated[str, Field(alias="infraArchType")]


class CIModuleInfo(BaseModel):
    ci_edition_type: t.Annotated[t.Optional[str], Field(alias="ciEditionType")] = None
    ci_license_type: t.Annotated[t.Optional[str], Field(alias="ciLicenseType")] = None
    image_details_list: t.Annotated[
        t.List[CIImageDetails], Field(alias="imageDetailsList")
    ] = []
    infra_details_list: t.Annotated[
        t.List[CIInfraDetails], Field(alias="infraDetailsList")
    ] = []
    is_private_repo: t.Annotated[bool, Field(alias="isPrivateRepo")] = False
    scm_details_list: t.Annotated[t.List[t.Any], Field(alias="scmDetailsList")] = []
    ti_build_details_list: t.Annotated[
        t.List[t.Any], Field(alias="tiBuildDetailsList")
    ] = []


class ModuleInfo(BaseModel):
    ci: t.Annotated[t.Optional[CIModuleInfo], Field(alias="ci")] = None


class FailureInfoDTO(BaseModel):
    message: str
    failure_type_list: t.Annotated[t.List[t.Any], Field(alias="failureTypeList")] = []
    response_messages: t.Annotated[t.List[t.Any], Field(alias="responseMessages")] = []


class NodeRunInfo(BaseModel):
    when_condition: t.Annotated[t.Optional[str], Field(alias="whenCondition")] = None
    evaluated_condition: t.Annotated[
        t.Optional[bool], Field(alias="evaluatedCondition")
    ] = None
    expressions: t.List[dict] = []


class EdgeLayoutList(BaseModel):
    current_node_children: t.Annotated[
        t.List[str], Field(alias="currentNodeChildren")
    ] = []
    next_ids: t.Annotated[t.List[str], Field(alias="nextIds")] = []


class LayoutNode(BaseModel):
    node_type: t.Annotated[str, Field(alias="nodeType")]
    node_group: t.Annotated[str, Field(alias="nodeGroup")]
    node_identifier: t.Annotated[str, Field(alias="nodeIdentifier")]
    name: str
    node_uuid: t.Annotated[str, Field(alias="nodeUuid")]
    status: str
    module: t.Annotated[t.Optional[str], Field(alias="module")] = None
    module_info: t.Annotated[t.Optional[ModuleInfo], Field(alias="moduleInfo")] = None
    start_ts: t.Annotated[t.Optional[datetime], Field(alias="startTs")] = None
    end_ts: t.Annotated[t.Optional[datetime], Field(alias="endTs")] = None

    @field_validator("start_ts", "end_ts", mode="before")
    @classmethod
    def convert_epoch_to_datetime(cls, ts: t.Any):
        if isinstance(ts, (float, int)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return ts

    edge_layout_list: t.Annotated[EdgeLayoutList, Field(alias="edgeLayoutList")] = (
        EdgeLayoutList()
    )
    node_run_info: t.Annotated[t.Optional[NodeRunInfo], Field(alias="nodeRunInfo")] = (
        None
    )
    failure_info: t.Annotated[t.Dict[str, t.Any], Field(alias="failureInfo")] = {}
    failure_info_dto: t.Annotated[
        t.Optional[FailureInfoDTO], Field(alias="failureInfoDTO")
    ] = None
    node_execution_id: t.Annotated[t.Optional[str], Field(alias="nodeExecutionId")] = (
        None
    )
    execution_input_configured: t.Annotated[
        bool, Field(alias="executionInputConfigured")
    ] = True
    is_rollback_stage_node: t.Annotated[bool, Field(alias="isRollbackStageNode")] = (
        False
    )


class ParentStageInfo(BaseModel):
    hasparentpipeline: bool
    stagenodeid: str
    executionid: str
    identifier: str
    projectid: str
    orgid: str
    runsequence: int


class PipelineExecutionSummary(BaseModel):
    pipeline_identifier: t.Annotated[str, Field(alias="pipelineIdentifier")]
    org_identifier: t.Annotated[str, Field(alias="orgIdentifier")]
    project_identifier: t.Annotated[str, Field(alias="projectIdentifier")]
    plan_execution_id: t.Annotated[str, Field(alias="planExecutionId")]
    name: str
    yaml_version: t.Annotated[str, Field(alias="yamlVersion")] = "0"
    status: str
    tags: t.List[t.Any] = []
    labels: t.List[t.Any] = []
    execution_trigger_info: t.Annotated[
        ExecutionTriggerInfo, Field(alias="executionTriggerInfo")
    ]
    governance_metadata: t.Annotated[
        t.Optional[GovernanceMetadata], Field(alias="governanceMetadata")
    ] = None
    module_info: t.Annotated[t.Optional[ModuleInfo], Field(alias="moduleInfo")] = None
    layout_node_map: t.Annotated[
        t.Dict[str, LayoutNode], Field(alias="layoutNodeMap")
    ] = {}
    modules: t.List[str]
    starting_node_id: t.Annotated[str, Field(alias="startingNodeId")]
    start_ts: t.Annotated[datetime, Field(alias="startTs")]
    end_ts: t.Annotated[t.Optional[datetime], Field(alias="endTs")] = None

    @field_validator("start_ts", "end_ts", mode="before")
    @classmethod
    def convert_epoch_to_datetime(cls, ts: t.Any):
        if isinstance(ts, (float, int)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return ts

    created_at: t.Annotated[int, Field(alias="createdAt")]
    can_retry: t.Annotated[bool, Field(alias="canRetry")] = False
    can_re_execute: t.Annotated[bool, Field(alias="canReExecute")] = False
    show_retry_history: t.Annotated[bool, Field(alias="showRetryHistory")] = False
    run_sequence: t.Annotated[int, Field(alias="runSequence")]
    successful_stages_count: t.Annotated[int, Field(alias="successfulStagesCount")] = 0
    running_stages_count: t.Annotated[int, Field(alias="runningStagesCount")] = 0
    failed_stages_count: t.Annotated[int, Field(alias="failedStagesCount")] = 0
    total_stages_count: t.Annotated[int, Field(alias="totalStagesCount")] = 0
    store_type: t.Annotated[str, Field(alias="storeType")] = "INLINE"
    execution_input_configured: t.Annotated[
        bool, Field(alias="executionInputConfigured")
    ] = True
    parent_stage_info: t.Annotated[
        t.Optional[ParentStageInfo], Field(alias="parentStageInfo")
    ] = None
    allow_stage_executions: t.Annotated[bool, Field(alias="allowStageExecutions")] = (
        False
    )
    execution_mode: t.Annotated[str, Field(alias="executionMode")]
    notes_exist_for_plan_execution_id: t.Annotated[
        bool, Field(alias="notesExistForPlanExecutionId")
    ] = False
    should_use_simplified_key: t.Annotated[
        bool, Field(alias="shouldUseSimplifiedKey")
    ] = False
    stages_execution: t.Annotated[bool, Field(alias="stagesExecution")] = False


class ExecutionGraphNode(BaseModel):
    uuid: t.Annotated[str, Field(alias="uuid")]
    setup_id: t.Annotated[str, Field(alias="setupId")]
    name: t.Annotated[str, Field(alias="name")]
    identifier: t.Annotated[str, Field(alias="identifier")]
    base_fqn: t.Annotated[str, Field(alias="baseFqn")]
    outcomes: t.Annotated[t.Dict[str, t.Any], Field(alias="outcomes")] = {}
    step_parameters: t.Annotated[t.Dict[str, t.Any], Field(alias="stepParameters")] = {}
    start_ts: t.Annotated[t.Optional[datetime], Field(alias="startTs")] = None
    end_ts: t.Annotated[t.Optional[datetime], Field(alias="endTs")] = None

    @field_validator("start_ts", "end_ts", mode="before")
    @classmethod
    def convert_epoch_to_datetime(cls, ts: t.Any):
        if isinstance(ts, (float, int)):
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return ts

    step_type: t.Annotated[str, Field(alias="stepType")]
    status: t.Annotated[str, Field(alias="status")]
    failure_info: t.Annotated[t.Dict[str, t.Any], Field(alias="failureInfo")] = {}
    skip_info: t.Annotated[t.Optional[t.Dict[str, t.Any]], Field(alias="skipInfo")] = (
        None
    )
    node_run_info: t.Annotated[t.Optional[NodeRunInfo], Field(alias="nodeRunInfo")] = (
        None
    )
    executable_responses: t.Annotated[
        t.List[t.Dict[str, t.Any]], Field(alias="executableResponses")
    ] = []
    unit_progresses: t.Annotated[
        t.List[t.Dict[str, t.Any]], Field(alias="unitProgresses")
    ] = []
    progress_data: t.Annotated[t.Dict[str, t.Any], Field(alias="progressData")] = {}
    delegate_info_list: t.Annotated[
        t.List[t.Dict[str, t.Any]], Field(alias="delegateInfoList")
    ] = []
    interrupt_histories: t.Annotated[
        t.List[t.Dict[str, t.Any]], Field(alias="interruptHistories")
    ] = []
    step_details: t.Annotated[t.Dict[str, t.Any], Field(alias="stepDetails")] = {}
    strategy_metadata: t.Annotated[
        t.Dict[str, t.Any], Field(alias="strategyMetadata")
    ] = {}

    @field_validator(
        "strategy_metadata",
        "step_details",
        "failure_info",
        "step_parameters",
        mode="before",
    )
    @classmethod
    def uniform_empty_dicts(cls, v: t.Any):
        if not v:
            return {}
        return v

    execution_input_configured: t.Annotated[
        bool, Field(alias="executionInputConfigured")
    ] = True
    log_base_key: t.Annotated[t.Optional[str], Field(alias="logBaseKey")]


class ExecutionGraph(BaseModel):
    root_node_id: t.Annotated[str, Field(alias="rootNodeId")]
    node_map: t.Annotated[t.Dict[str, ExecutionGraphNode], Field(alias="nodeMap")] = {}
    node_adjacency_list_map: t.Annotated[
        t.Dict[str, t.Any], Field(alias="nodeAdjacencyListMap")
    ] = {}


class ExecutionMetadata(BaseModel):
    account_id: t.Annotated[str, Field(alias="accountId")]
    pipeline_identifier: t.Annotated[str, Field(alias="pipelineIdentifier")]
    org_identifier: t.Annotated[str, Field(alias="orgIdentifier")]
    project_identifier: t.Annotated[str, Field(alias="projectIdentifier")]
    plan_execution_id: t.Annotated[str, Field(alias="planExecutionId")]


class PipelineExecution(BaseModel):
    pipeline_execution_summary: t.Annotated[
        PipelineExecutionSummary, Field(alias="pipelineExecutionSummary")
    ]
    execution_graph: t.Annotated[ExecutionGraph, Field(alias="executionGraph")]
    execution_metadata: t.Annotated[
        t.Optional[ExecutionMetadata], Field(alias="executionMetadata")
    ] = None
    representation_strategy: t.Annotated[str, Field(alias="representationStrategy")] = (
        "camelCase"
    )
