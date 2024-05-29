"""A simple wrapper around the Harness API for managing pipelines."""

import typing as t
import warnings

import requests

import harness_tui.models as M
from harness_tui.api.mixin import ClientMixin
from harness_tui.utils import ttl_cache


def _strip_unset(kwargs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """Remove unset values from a dictionary."""
    return {k: v for k, v in kwargs.items() if v is not None}


class PipelineClient(ClientMixin):
    BASE_URL = "https://app.harness.io/pipeline/api/"

    def __init__(
        self,
        session: requests.Session,
        /,
        *,
        account: str,
        org: str,
        project: str,
    ) -> None:
        """A wrapper around the Harness API for managing pipelines.

        Args:
            api_key (str): The Harness API key.
            account (str): The Harness account identifier.
            org (str): The Harness organization identifier.
            project (str): The Harness project identifier.
            session (requests.Session): An authenticated requests session.
        """
        self.session = session
        self.account = account
        self.org = org
        self.project = project

    # @ttl_cache(10)
    def list(
        self,
        filter_type: str = "PipelineSetup",
        page: int = 0,
        size: int = 25,
        sort: t.Optional[str] = None,
        search_term: t.Optional[str] = None,
        module: t.Optional[str] = None,
        filter_identifier: t.Optional[str] = None,
        branch: t.Optional[str] = None,
        repo_identifier: t.Optional[str] = None,
        get_default_from_other_repo: bool = False,
        get_distinct_from_branches: bool = False,
    ) -> t.List[M.PipelineSummary]:
        """List pipelines."""
        _ = filter_type
        pipelines = self._request(
            "POST",
            "pipelines/list",
            params=_strip_unset(
                {
                    "accountIdentifier": self.account,
                    "orgIdentifier": self.org,
                    "projectIdentifier": self.project,
                    "page": page,
                    "size": size,
                    "sort": sort,
                    "searchTerm": search_term,
                    "module": module,
                    "filterIdentifier": filter_identifier,
                    "branch": branch,
                    "repoIdentifier": repo_identifier,
                    "getDefaultFromOtherRepo": get_default_from_other_repo,
                    "getDistinctFromBranches": get_distinct_from_branches,
                }
            ),
        )["data"]["content"]
        return list(map(M.PipelineSummary.model_validate, pipelines))

    def reference(self, pipeline_identifier: str) -> "PipelineReference":
        """Get a reference to a specific pipeline."""
        return PipelineReference(self, pipeline_identifier)


class PipelineReference:
    def __init__(
        self,
        client: PipelineClient,
        pipeline_identifier: str,
    ) -> None:
        """A wrapper around a Harness pipeline.

        Args:
            client (PipelineClient): The client to use for API requests.
            pipeline_identifier (str): The identifier of the pipeline.
        """
        self.client = client
        self.pipeline_identifier = pipeline_identifier

    @ttl_cache(60)
    def summary(
        self,
        branch: t.Optional[str] = None,
        repo_identifier: t.Optional[str] = None,
        get_default_from_other_repo: bool = False,
        load_from_fallback_branch: bool = False,
    ) -> M.PipelineSummary:
        """Get a summary of the pipeline."""
        return M.PipelineSummary.model_validate(
            self.client._request(
                "GET",
                f"pipelines/summary/{self.pipeline_identifier}",
                headers={"Load-From-Cache": "false"},
                params=_strip_unset(
                    {
                        "accountIdentifier": self.client.account,
                        "orgIdentifier": self.client.org,
                        "projectIdentifier": self.client.project,
                        "branch": branch,
                        "repoIdentifier": repo_identifier,
                        "getDefaultFromOtherRepo": get_default_from_other_repo,
                        "loadFromFallbackBranch": load_from_fallback_branch,
                    }
                ),
            )["data"]
        )

    @ttl_cache(60)
    def get(
        self,
        branch: t.Optional[str] = None,
        repo_identifier: t.Optional[str] = None,
        get_default_from_other_repo: bool = False,
        load_from_fallback_branch: bool = False,
    ) -> M.Pipeline:
        """Get the pipeline."""
        return M.Pipeline.model_validate(
            self.client._request(
                "GET",
                f"pipelines/{self.pipeline_identifier}",
                headers={"Load-From-Cache": "false"},
                params=_strip_unset(
                    {
                        "accountIdentifier": self.client.account,
                        "orgIdentifier": self.client.org,
                        "projectIdentifier": self.client.project,
                        "branch": branch,
                        "repoIdentifier": repo_identifier,
                        "getDefaultFromOtherRepo": get_default_from_other_repo,
                        "loadFromFallbackBranch": load_from_fallback_branch,
                    }
                ),
            )["data"]
        )

    def definition(self, **kwargs: t.Any) -> t.Dict[str, t.Any]:
        info = self.get(**kwargs)
        return info.resolved_template_pipeline_dict or info.pipeline_dict

    def update(
        self,
        pipeline_yaml: str,
        name: str,
        description: t.Optional[str] = None,
        tags: t.Optional[t.Dict[str, str]] = None,
        git_details: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """Update the pipeline."""
        warnings.warn(
            "Update is a no-op for development purposes. This will be enabled later.",
            FutureWarning,
        )
        return {}
        return self.client._request(
            "PUT",
            f"pipelines/{self.client.org}/{self.client.project}/{self.pipeline_identifier}",
            json=_strip_unset(
                {
                    "pipeline_yaml": pipeline_yaml,
                    "identifier": self.pipeline_identifier,
                    "name": name,
                    "description": description,
                    "tags": tags,
                    "git_details": git_details,
                }
            ),
        )

    def execute(
        self,
        inputs_yaml: t.Optional[str] = None,
        module: t.Optional[str] = None,
        use_fqn_if_error_response: bool = False,
        notify_only_user: bool = False,
        notes: t.Optional[str] = None,
        branch_name: t.Optional[str] = None,
        connector_ref: t.Optional[str] = None,
        repo_name: t.Optional[str] = None,
    ):
        """Execute the pipeline."""
        warnings.warn(
            "Execute is a no-op for development purposes. This will be enabled later.",
            FutureWarning,
        )
        return {}
        return self.client._request(
            "POST",
            f"orgs/{self.client.org}/projects/{self.client.project}/pipelines/{self.pipeline_identifier}/execute",
            json=_strip_unset(
                {
                    "inputs_yaml": inputs_yaml,
                    "module": module,
                    "use_fqn_if_error_response": use_fqn_if_error_response,
                    "notify_only_user": notify_only_user,
                    "notes": notes,
                    "branch_name": branch_name,
                    "connector_ref": connector_ref,
                    "repo_name": repo_name,
                }
            ),
        )
