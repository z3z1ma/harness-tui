"""Defines the Pydantic model for a pipeline."""

import typing as t
from datetime import datetime, timezone

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


class Pipeline(BaseModel):
    pipeline_yaml: t.Annotated[t.Dict[str, t.Any], Field(alias="yamlPipeline")]
    resolved_template_pipeline_yaml: t.Annotated[
        t.Dict[str, t.Any], Field(alias="resolvedTemplatePipelineYaml")
    ]
    git_details: t.Annotated[t.Optional[GitDetails], Field(alias="gitDetails")] = None
    entity_validity: t.Annotated[
        EntityValidityDetails, Field(alias="entityValidityDetails")
    ]
    modules: t.List[str]
    validation_uuid: t.Annotated[str, Field(alias="validationUuid")]
    store_type: t.Annotated[str, Field(alias="storeType")] = "INLINE"
    public_access: t.Annotated[
        t.Optional[PublicAccess], Field(alias="publicAccessResponse")
    ] = None
