import json 
import sys 
import requests 
import os
from dotenv import load_dotenv

# 공용 환경변수 로드
load_dotenv(".env.common", override=True)

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

# 슬랙 메세지 틀 작성
def send_result_to_slack(total_products, successful_products, failed_products):
    total_products = len(total_products)
    success_count = len(successful_products)
    fail_count = len(failed_products)

    failed_message = ", ".join(map(str, failed_products)) if failed_products else "모든 상품의 데이터를 성공적으로 추출했습니다."
    
    result_title = "🌟 상품 가격 추출 결과 🌟"
    result_message = (
        f"총 상품 수: {total_products}\n"
        f"성공적으로 추출된 상품 수: {success_count}\n"
        f"실패한 상품 수: {fail_count}\n\n"
        f"❗️*추출결과*\n{failed_message}"
    )
    send_slack_message(result_title, result_message)