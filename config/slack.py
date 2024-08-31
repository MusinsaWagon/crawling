import json 
import sys 
import requests 
import os
from dotenv import load_dotenv

load_dotenv() # 환경변수 로딩

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(title, message):
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title, 
                        "value": message, 
                        "short": False
                    }
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_data), headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")


