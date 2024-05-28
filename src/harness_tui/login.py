import base64
import json

import requests


def login_to_harness(environment_url, username, password):
    # Encode the username and password in base64
    auth_string = f"{username}:{password}"
    auth_encoded = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    # Prepare the payload
    payload = {"authorization": f"Basic {auth_encoded}"}

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Make the POST request
    response = requests.post(
        f"{environment_url}/api/users/login", headers=headers, data=json.dumps(payload)
    )

    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()

        user_id = response_json.get("resource", {}).get("uuid")
        account_id = response_json.get("resource", {}).get("defaultAccountId")
        token = response_json.get("resource", {}).get("token")

        return {"user_id": user_id, "account_id": account_id, "token": token}
    else:
        raise Exception(f"Failed to login: {response.status_code} - {response.text}")


# Example usage
environment_url = "https://app.harness.io"  # Replace with your actual URL
username = "your_username"  # Replace with your actual username
password = "your_password"  # Replace with your actual password

login_info = login_to_harness(environment_url, username, password)
print("Login info:", login_info)
