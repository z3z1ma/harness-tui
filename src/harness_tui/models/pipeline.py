"""Defines the Pydantic model for a pipeline."""

import typing as t

from pydantic import BaseModel, Field


class ExecutionSummaryInfo(BaseModel):
    number_of_errors: t.Annotated[t.List[int], Field(alias="numOfErrors")]
    deployments: t.List[int]
    last_execution_ts: t.Annotated[int, Field(alias="lastExecutionTs")]
    last_execution_status: t.Annotated[str, Field(alias="lastExecutionStatus")]
    last_execution_id: t.Annotated[str, Field(alias="lastExecutionId")]


class GitDetails(BaseModel):
    valid: bool = True
    invalid_yaml: t.Annotated[t.Optional[str], Field(alias="invalidYaml")] = None


class EntityValidityDetails(BaseModel):
    valid: bool = True
    invalid_yaml: t.Annotated[t.Optional[str], Field(alias="invalidYaml")] = None


class Pipeline(BaseModel):
    name: str
    identifier: str
    description: str = ""
    tags: t.Dict[str, str] = {}
    version: int = 0
    number_of_stages: t.Annotated[int, Field(alias="numOfStages")]
    created_at: t.Annotated[int, Field(alias="createdAt")]
    last_updated_at: t.Annotated[int, Field(alias="lastUpdatedAt")]
    modules: t.List[str]
    execution_summary_info: t.Annotated[
        ExecutionSummaryInfo, Field(alias="executionSummaryInfo")
    ]
    filters: t.Dict[str, t.Any]
    stage_names: t.Annotated[t.List[str], Field(alias="stageNames")]
    git_details: t.Annotated[t.Optional[GitDetails], Field(alias="gitDetails")] = None
    entity_validity_details: t.Annotated[
        EntityValidityDetails, Field(alias="entityValidityDetails")
    ]
    store_type: t.Annotated[str, Field(alias="storeType")] = "INLINE"
    connector_ref: t.Annotated[t.Optional[str], Field(alias="connectorRef")] = None
    is_draft: t.Annotated[bool, Field(alias="isDraft")] = False
    yaml_version: t.Annotated[str, Field(alias="yamlVersion")] = "0"

    class Config:
        populate_by_name = True
