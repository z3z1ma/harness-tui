import os

import requests
import requests.adapters

from harness_tui.api.pipeline import PipelineClient


class HarnessClient:
    """Client for interacting with the Harness API."""

    def __init__(self, api_key: str, account: str, org: str, project: str):
        self.api_key = api_key
        self.account = account
        self.org = org
        self.project = project
        session = requests.Session()
        session.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount("https://", adapter)
        self.session = session
        self.pipelines = PipelineClient(
            session, account=account, org=org, project=project
        )

    @classmethod
    def default(cls) -> "HarnessClient":
        """Create a default instance of the class from environment variables."""
        return cls(
            api_key=os.environ["HARNESS_API_KEY"],
            account=os.environ["HARNESS_ACCOUNT"],
            org=os.environ["HARNESS_ORG"],
            project=os.environ["HARNESS_PROJECT"],
        )


__all__ = ["HarnessClient"]


# Example usage
if __name__ == "__main__":
    import rich

    client = HarnessClient.default()

    # Fetch list of pipelines
    pipelines = client.pipelines.list()
    # rich.print(pipelines)

    # Get pipeline reference
    pipeline = client.pipelines.reference("TimescaleDB_Pipeline")

    # Fetch pipeline summary
    # rich.print(pipeline.summary())

    # Fetch pipeline YAML
    rich.print(pipeline.executions())

    # Execute pipeline
    # execution_result = pipeline.execute()
    # rich.print(execution_result)

    exit(0)

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

    updated_pipeline = pipeline.update(
        pipeline_yaml, name, description, tags, git_details
    )
    print("Updated Pipeline:", updated_pipeline)

    # Execute pipeline
    inputs_yaml = "your-inputs-yaml"
    execution_result = pipeline.execute(inputs_yaml=inputs_yaml)
    print("Pipeline Execution Result:", execution_result)
    print("Pipeline Execution Result:", execution_result)
