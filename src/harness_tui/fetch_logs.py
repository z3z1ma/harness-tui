import requests
import urllib.parse

def fetch_logs():

    url = 'https://app.harness.io/gateway/log-service/blob'
    

    account_id = 'VRuJ8-dqQH6QZgAtoBr66g'
    org_id = 'default'
    pipeline_id = 'test'
    project_id = 'TESTINTELLIGENCEMASTER'
    run_sequence = '2'
    level0 = 'pipeline'
    level1 = 'stages'
    level2 = 'test'
    level3 = 'spec'
    level4 = 'execution'
    level5 = 'steps'
    level6 = 'ShellScript_1-commandUnit'
    

    key_components = [
        f'accountId:{account_id}',
        f'orgId:{org_id}',
        f'projectId:{project_id}',
        f'pipelineId:{pipeline_id}',
        f'runSequence:{run_sequence}',
        f'level0:{level0}',
        f'level1:{level1}',
        f'level2:{level2}',
        f'level3:{level3}',
        f'level4:{level4}',
        f'level5:{level5}',
        f'level6:{level6}'
    ]
    

    key = urllib.parse.quote('/'.join(key_components))
    

    params = {
        'accountID': account_id,
        'orgId': org_id,
        'pipelineId': pipeline_id,
        'projectId': project_id,
        'key': key
    }
    

    headers = {
        'accept': '*/*',
        'authorization': 'Bearer <JWT_TOKEN>',
        'content-type': 'application/json'
    }


    response = requests.get(url, headers=headers, params=params)
    

    if response.status_code == 200:
        print("Logs fetched successfully")
        print(response.text)  
    else:
        print(f"Failed to fetch logs: {response.status_code}")
        print(response.text)


fetch_logs()
