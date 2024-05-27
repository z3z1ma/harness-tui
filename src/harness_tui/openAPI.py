import requests

def list_pipelines(api_key, account_identifier, org_identifier, project_identifier, filter_type="PipelineSetup", page=0, size=25, sort=None, search_term=None, module=None, filter_identifier=None, branch=None, repo_identifier=None, get_default_from_other_repo=False, get_distinct_from_branches=False):
    url = 'https://app.harness.io/pipeline/api/pipelines/list'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    payload = {
        "accountIdentifier": account_identifier,
        "orgIdentifier": org_identifier,
        "projectIdentifier": project_identifier,
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
        "getDistinctFromBranches": get_distinct_from_branches
    }

    # Remove None values from payload
    payload = {k: v for k, v in payload.items() if v is not None}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_pipeline_summary(api_key, pipeline_identifier, account_identifier, org_identifier, project_identifier, branch=None, repo_identifier=None, get_default_from_other_repo=False, load_from_fallback_branch=False):
    url = f'https://app.harness.io/pipeline/api/pipelines/summary/{pipeline_identifier}'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'Load-From-Cache': 'false'
    }
    params = {
        "accountIdentifier": account_identifier,
        "orgIdentifier": org_identifier,
        "projectIdentifier": project_identifier,
        "branch": branch,
        "repoIdentifier": repo_identifier,
        "getDefaultFromOtherRepo": get_default_from_other_repo,
        "loadFromFallbackBranch": load_from_fallback_branch
    }

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def update_pipeline(api_key, org_identifier, project_identifier, pipeline_identifier, pipeline_yaml, name, description, tags=None, git_details=None):
    url = f'https://app.harness.io/pipeline/api/pipelines/{org_identifier}/{project_identifier}/{pipeline_identifier}'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'Harness-Account': account_identifier
    }
    payload = {
        "pipeline_yaml": pipeline_yaml,
        "identifier": pipeline_identifier,
        "name": name,
        "description": description,
        "tags": tags or {},
        "git_details": git_details or {}
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def execute_pipeline(org, project, pipeline, api_key, inputs_yaml=None, module=None, use_fqn_if_error_response=False, notify_only_user=False, notes=None, branch_name=None, connector_ref=None, repo_name=None):
    url = f"https://app.harness.io/pipeline/api/orgs/{org}/projects/{project}/pipelines/{pipeline}/execute"
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'Harness-Account': 'your-harness-account-id'  # Replace with your actual account ID if necessary
    }
    
    payload = {
        "inputs_yaml": inputs_yaml,
        "module": module,
        "use_fqn_if_error_response": use_fqn_if_error_response,
        "notify_only_user": notify_only_user,
        "notes": notes,
        "branch_name": branch_name,
        "connector_ref": connector_ref,
        "repo_name": repo_name
    }
    
    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example usage
if __name__ == "__main__":
    api_key = 'YOUR_API_KEY'
    account_identifier = 'YOUR_ACCOUNT_IDENTIFIER'
    org_identifier = 'YOUR_ORG_IDENTIFIER'
    project_identifier = 'YOUR_PROJECT_IDENTIFIER'
    pipeline_identifier = 'YOUR_PIPELINE_IDENTIFIER'
    
    # Fetch list of pipelines
    pipelines = list_pipelines(api_key, account_identifier, org_identifier, project_identifier)
    print("Pipelines:", pipelines)
    
    # Fetch pipeline summary
    pipeline_summary = fetch_pipeline_summary(api_key, pipeline_identifier, account_identifier, org_identifier, project_identifier)
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
    tags = {"example-tag-1": "example-tag-1-value", "example-tag-2": "example-tag-2-value"}
    git_details = {
        "branch_name": "branch",
        "commit_message": "Added Harness Git Experience",
        "last_object_id": "abcdXYZ",
        "base_branch": "old_branch",
        "last_commit_id": "abcdXYZ",
        "connector_ref": "git_connector",
        "store_type": "REMOTE",
        "repo_name": "example_repository"
    }
    
    updated_pipeline = update_pipeline(api_key, org_identifier, project_identifier, pipeline_identifier, pipeline_yaml, name, description, tags, git_details)
    print("Updated Pipeline:", updated_pipeline)
    
    # Execute pipeline
    inputs_yaml = "your-inputs-yaml"
    execution_result = execute_pipeline(org_identifier, project_identifier, pipeline_identifier, api_key, inputs_yaml=inputs_yaml)
    print("Pipeline Execution Result:", execution_result)
