import os
import typing as t
from urllib.parse import urljoin, urlparse

import requests


def _strip_unset(kwargs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """Remove unset values from a dictionary."""
    return {k: v for k, v in kwargs.items() if v is not None}


class PipelineClient:
    BASE_URL = "https://app.harness.io/pipeline/api"

    def __init__(
        self,
        api_key: str,
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
        """
        self.api_key = api_key
        self.account = account
        self.org = org
        self.project = project
        self._session = None

    @classmethod
    def default(cls) -> "PipelineClient":
        """Create a default instance of the class from environment variables."""
        return cls(
            api_key=os.environ["HARNESS_API_KEY"],
            account=os.environ["HARNESS_ACCOUNT"],
            org=os.environ["HARNESS_ORG"],
            project=os.environ["HARNESS_PROJECT"],
        )

    @property
    def session(self) -> requests.Session:
        """A requests session with the necessary headers set."""
        if self._session is None:
            session = requests.Session()
            session.headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            }
            self._session = session
        return self._session

    def _request(
        self, method: t.Literal["GET", "POST", "PUT", "DELETE"], path: str, **kwargs
    ) -> t.Any:
        """Make a request to the Harness API.

        Args:
            method (str): The HTTP method to use.
            path (str): The path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Raises:
            requests.HTTPError: If the request fails.

        Returns:
            t.Any: The JSON response.
        """
        if not urlparse(path).scheme:
            path = urljoin(PipelineClient.BASE_URL, path)
        response = getattr(self.session, method.lower())(path, **kwargs)
        response.raise_for_status()
        return response.json()

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
    ):
        return self._request(
            "POST",
            "pipelines/list",
            json=_strip_unset(
                {
                    "accountIdentifier": self.account,
                    "orgIdentifier": self.org,
                    "projectIdentifier": self.project,
                    "page": page,
                    "size": size,
                    "filterType": filter_type,
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
        )

    def fetch_summary(
        self,
        pipeline_identifier: str,
        branch: t.Optional[str] = None,
        repo_identifier: t.Optional[str] = None,
        get_default_from_other_repo: bool = False,
        load_from_fallback_branch: bool = False,
    ):
        return self._request(
            "GET",
            f"pipelines/summary/{pipeline_identifier}",
            headers={"Load-From-Cache": "false"},
            params=_strip_unset(
                {
                    "accountIdentifier": self.account,
                    "orgIdentifier": self.org,
                    "projectIdentifier": self.project,
                    "branch": branch,
                    "repoIdentifier": repo_identifier,
                    "getDefaultFromOtherRepo": get_default_from_other_repo,
                    "loadFromFallbackBranch": load_from_fallback_branch,
                }
            ),
        )

    def update_pipeline(
        self,
        pipeline_identifier: str,
        pipeline_yaml: str,
        name: str,
        description: t.Optional[str] = None,
        tags: t.Optional[t.Dict[str, str]] = None,
        git_details: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        return self._request(
            "PUT",
            f"pipelines/{self.org}/{self.project}/{pipeline_identifier}",
            json=_strip_unset(
                {
                    "pipeline_yaml": pipeline_yaml,
                    "identifier": pipeline_identifier,
                    "name": name,
                    "description": description,
                    "tags": tags,
                    "git_details": git_details,
                }
            ),
        )

    def execute_pipeline(
        self,
        pipeline_identifier: str,
        inputs_yaml: t.Optional[str] = None,
        module: t.Optional[str] = None,
        use_fqn_if_error_response: bool = False,
        notify_only_user: bool = False,
        notes: t.Optional[str] = None,
        branch_name: t.Optional[str] = None,
        connector_ref: t.Optional[str] = None,
        repo_name: t.Optional[str] = None,
    ):
        return self._request(
            "POST",
            f"orgs/{self.org}/projects/{self.project}/pipelines/{pipeline_identifier}/execute",
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


# Example usage
if __name__ == "__main__":
    client = PipelineClient(
        api_key="YOUR_API_KEY",
        account="YOUR_ACCOUNT_IDENTIFIER",
        org="YOUR_ORG_IDENTIFIER",
        project="YOUR_PROJECT_IDENTIFIER",
    )

    pipeline_identifier = "YOUR_PIPELINE_IDENTIFIER"

    # Fetch list of pipelines
    pipelines = client.list()
    print("Pipelines:", pipelines)

    # Fetch pipeline summary
    pipeline_summary = client.fetch_summary(pipeline_identifier)
    print("Pipeline Summary:", pipeline_summary)

    # Update pipeline
    pipeline_yaml = """pipeline:
    identifier: example_pipeline
    name: ExamplePipeline
    allowStageExecutions: false
    stages:
        - stage:
            name: Example Build Stage
            identifier: example_build_stage
            description: ''
            type: Approval
            spec:
            execution:
                steps:
                - step:
                    name: Approval Step
                    identifier: Approval_Step
                    type: HarnessApproval
                    timeout: 1d
                    spec:
                        approvalMessage: |-
                        Please review the following information
                        and approve the pipeline progression
                        includePipelineExecutionHistory: true
                        approvers:
                        minimumCount: 1
                        disallowPipelineExecutor: false
                        userGroups: <+input>
                        approverInputs: []
                - step:
                    type: ShellScript
                    name: ShellScript Step
                    identifier: ShellScript_Step
                    spec:
                        shell: Bash
                        onDelegate: true
                        source:
                        type: Inline
                        spec:
                            script: <+input>
                        environmentVariables: []
                        outputVariables: []
                        executionTarget: {}
                    timeout: 10m
            tags: {}
        - stage:
            name: Example Deploy Stage
            identifier: example_deploy_stage
            description: ''
            type: Deployment
            spec:
            serviceConfig:
                serviceRef: <+input>
                serviceDefinition:
                spec:
                    variables: []
                type: Kubernetes
            infrastructure:
                environmentRef: <+input>
                infrastructureDefinition:
                type: KubernetesDirect
                spec:
                    connectorRef: <+input>
                    namespace: <+input>
                    releaseName: release-<+INFRA_KEY>
                allowSimultaneousDeployments: false
            execution:
                steps:
                - step:
                    name: Rollout Deployment
                    identifier: rolloutDeployment
                    type: K8sRollingDeploy
                    timeout: 10m
                    spec:
                        skipDryRun: false
                rollbackSteps:
                - step:
                    name: Rollback Rollout Deployment
                    identifier: rollbackRolloutDeployment
                    type: K8sRollingRollback
                    timeout: 10m
                    spec: {}
            tags: {}
            failureStrategies:
            - onFailure:
                errors:
                    - AllErrors
                action:
                    type: StageRollback
    """
    name = "ExamplePipeline"
    description = "Pipeline Description"
    tags = {
        "example-tag-1": "example-tag-1-value",
        "example-tag-2": "example-tag-2-value",
    }
    git_details = {
        "branch_name": "branch",
        "commit_message": "Added Harness Git Experience",
        "last_object_id": "abcdXYZ",
        "base_branch": "old_branch",
        "last_commit_id": "abcdXYZ",
        "connector_ref": "git_connector",
        "store_type": "REMOTE",
        "repo_name": "example_repository",
    }

    updated_pipeline = client.update_pipeline(
        pipeline_identifier,
        pipeline_yaml,
        name,
        description,
        tags,
        git_details,
    )
    print("Updated Pipeline:", updated_pipeline)

    # Execute pipeline
    inputs_yaml = "your-inputs-yaml"
    execution_result = client.execute_pipeline(
        pipeline_identifier, inputs_yaml=inputs_yaml
    )
    print("Pipeline Execution Result:", execution_result)
