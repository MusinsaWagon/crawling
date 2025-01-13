import json 
import sys 
import requests 
import os
from dotenv import load_dotenv

# 공용 환경변수 로드
load_dotenv(".env.common")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(title, message):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL is not set. Please check your environment variables.")
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

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_data), headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
        
        print("Message successfully sent to Slack")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Slack: {e}")
        sys.exit(1)
