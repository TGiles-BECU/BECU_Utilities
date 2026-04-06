import requests
from requests.auth import HTTPBasicAuth
import json
import os
from pathlib import Path

from dotenv import load_dotenv
current_file_dir = Path(__file__).resolve().parent.parent
env_path = current_file_dir / '.env'
load_dotenv(dotenv_path=env_path)

def test(): return os.getenv("JSM_EMAIL")

import logging
logger = logging.getLogger(__name__)

def open(issueSummary, issueDescritpion, issuePriority=3):

    # Jira credentials and endpoint
    JIRA_URL = os.getenv("JSM_URL")
    EMAIL = os.getenv("JSM_EMAIL")
    # The below API token expires every year, this on expires 4/23/2026
    API_TOKEN = os.getenv("JSM_API_KEY")
    PROJECT_KEY = "BHD"  # Change to your project key
    SERVICE_DESK_ID = "6" # Portal ID number
    REQUEST_TYPE_ID = "453"  # Change this to your JSM request type ID
    # ID found in URL under project/space > settings > request types > *type that you want*
    # Sandbox example: key=SB id=189 serviceDeskId=12

    # REST API endpoint for creating customer requests
    url = f"{JIRA_URL}/rest/servicedeskapi/request"

    # Headers
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Request payload
    payload = json.dumps({
        "serviceDeskId": SERVICE_DESK_ID,
        "requestTypeId": REQUEST_TYPE_ID,
        "requestFieldValues": {
            "summary": issueSummary,
            "description": issueDescritpion,
            "priority": { "id": str(issuePriority) }
            # Priority id's:
            # '10001' = Notification
            # '4' = Low
            # '3' = Medium
            # '2' = High
            # '10000' = Urgent
        }
    })

    # Send request
    response = requests.post(
        url,
        data=payload,
        headers=headers,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN)
    )

    # Output result
    if response.status_code == 201:
        print("✅ Issue created successfully!")
        print(response.json())
        issueKey = response.json()['issueKey']
        return issueKey
    else:
        print(f"❌ Failed to create issue: {response.status_code}")
        print(response.text)