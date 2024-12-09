import os

import arrow
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from kurly import clusters

# 환경 변수에서 Slack 토큰, 채널을 로드
load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

def send_slack_message(message, channel):
    try:
        client = WebClient(token=SLACK_TOKEN)
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message to {channel} : {e}")

def main():
    for cluster in clusters:
        
        # 메시지 제목 설정
        header = f"📢*《 김포 인사총무팀 공지 》*\n\n"
            
        notice_msg = (
            f"안녕하세요. 김포 클러스터 구성원 여러분 \n\n"
            f"인사총무팀에서 안내드립니다.\n"
            f"✔ 센터 내 흡연은 지정된 흡연장에서만 🚭\n"
            f"✔ 센터 내 차량 주행 시 반드시 20km/h이하로 서행 🚗\n"
            f"✔ 온도 관리를 위하여 방열문 및 오버헤드도어 미 사용 시 Close 🌡\n"
            f"✔ 지게차 운전 시 항상 안전운전!! 방어운전!! 🦺\n\n"
            f"🚨 시설물 관련 이슈 발생 시 *#11_시설안전이슈_김포* 채널에 공유 부탁드립니다.\n"
            f"감사합니다.\n"
            f"*첨부 - <https://static.wixstatic.com/media/70b014_af73a48c252a4a019d141818de2fe736~mv2.png공지사항>*\n"
        )

        # 메시지 본문
        body = header + notice_msg
    
        # 슬랙 채널에 전송
        send_slack_message(body, cluster.channel)

if __name__ == "__main__":
    main()
