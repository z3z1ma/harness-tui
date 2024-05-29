import requests
import sseclient


def fetch_logs():
    account_id = "HimkkTyJRZ6ryG5YRlCKUQ"
    org_id = "default"
    project_id = "DataOps_Platform"
    pipeline_id = "Dummy"
    run_sequence = "12"

    level0 = "pipeline"
    level1 = "stages"
    level2 = "SlowLog"
    level3 = "spec"
    level4 = "execution"
    level5 = "steps"
    level6 = "DoStuff-commandUnit:Execute"  # -commandUnit:Execute for custom stage / CD shell step?

    log_service_token = requests.get(
        "https://app.harness.io/gateway/log-service/token",
        params={"accountID": account_id},
        headers={"X-Api-Key": "..."},
    ).text

    key_components = [
        f"accountId:{account_id}",
        f"orgId:{org_id}",
        f"projectId:{project_id}",
        f"pipelineId:{pipeline_id}",
        f"runSequence:{run_sequence}",
        f"level0:{level0}",
        f"level1:{level1}",
        f"level2:{level2}",
        f"level3:{level3}",
        f"level4:{level4}",
        f"level5:{level5}",
        f"level6:{level6}",
    ]

    response = requests.get(
        "https://app.harness.io/gateway/log-service/stream",
        headers={
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Harness-Token": log_service_token,
        },
        params={
            "accountID": account_id,
            "X-Harness-Token": "",
            "key": "/".join(key_components),
        },
        allow_redirects=True,
        stream=True,
    )
    # print(response.request.url)

    if response.status_code == 200:
        print("Logs fetched successfully")
        for sse in sseclient.SSEClient(response).events():  # type: ignore
            if sse.event == "ping":
                continue
            elif sse.event == "error":
                if sse.data.upper() == "EOF":
                    break
                else:
                    raise Exception(f"Error streaming logs: {sse.data}")
            else:
                print(sse.data)
    else:
        print(f"Failed to fetch logs: {response.status_code}")
        print(response.text)


fetch_logs()
