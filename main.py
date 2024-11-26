import os

import arrow
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from kurly import clusters

import weather

# 환경 변수에서 Slack 토큰, 채널을 로드
load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

STATUS_OF_SKY = {
    '1': '☀️ ',
    '3': '☁️ ',
    '4': '⛅️ ',
}

STATUS_OF_PRECIPITATION = {
    '1': '🌧️ 비',
    '2': '🌨️ 비/눈',
    '3': '❄️ 눈',
    '4': '☔️ 소나기'
}

def send_slack_message(message, channel):
    try:
        client = WebClient(token=SLACK_TOKEN)
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message to {channel} : {e}")

def main():
    for cluster in clusters:
        # 현재 날짜 (KST 기준)
        current_time_kst = arrow.now('Asia/Seoul')
        
        date_format = "YYYY년 MM월 DD일 dddd"
        date_of_today = current_time_kst.format(date_format, locale="ko_kr")
    
        # 날씨 정보
        sky = weather.fetch_data_from_kma(current_time_kst, 'SKY', '0800', cluster.nx, cluster.ny)
        precipitation = weather.fetch_data_from_kma(current_time_kst, 'PTY', current_time_kst.format("HH00"), cluster.nx, cluster.ny)
        humidity_of_today = weather.fetch_data_from_kma(current_time_kst, 'REH', current_time_kst.format("HH00"), cluster.nx, cluster.ny)
        lowest_temp_of_today = weather.fetch_data_from_kma(current_time_kst, 'TMN', '0600', cluster.nx, cluster.ny)
        highest_temp_of_today = weather.fetch_data_from_kma(current_time_kst, 'TMX', '1500', cluster.nx, cluster.ny)
        precipitation_of_today = weather.fetch_data_from_kma(current_time_kst, 'PCP', current_time_kst.format("HH00"), cluster.nx, cluster.ny)
        snowfall_of_today = weather.fetch_data_from_kma(current_time_kst, 'SNO', current_time_kst.format("HH00"), cluster.nx, cluster.ny)
        weendspeed_of_today = weather.fetch_data_from_kma(current_time_kst, 'WSD', current_time_kst.format("HH00"), cluster.nx, cluster.ny)
        
        # 최고 기온과 금일 습도를 가지고 체감 온도를 계산
        highest_temp = float(highest_temp_of_today)  # 최고 기온을 실수형으로 변환
        humidity = int(humidity_of_today)  # 금일 습도를 정수형으로 변환

        # 금일 습도에 따라 체감 온도 계산
        if humidity == 50:
            perceived_temp = highest_temp
        elif humidity > 50:
            perceived_temp = highest_temp + ((humidity - 50) // 10)
        else:  # humidity_percent < 50
            perceived_temp = highest_temp - ((50 - humidity) // 10)
    
        # 날씨 상태 정보 설정
        sky_status = STATUS_OF_SKY.get(sky, '알 수 없음')
        precipitation_status = STATUS_OF_PRECIPITATION.get(precipitation, None)
        
        # 날씨 상태에 따라 메시지 제목 설정
        if precipitation_status is not None:
            weather_of_today = f"{precipitation_status}"
        else:
            weather_of_today = f"{sky_status}"
        
        # 강수량이 '강수없음'이거나 0일 경우를 처리
        if precipitation in ['-', 'null', '0']:
            precipitation_of_today = 0
        
        # 이후 코드에서는 precipitation_of_today가 0인지 확인하여 처리
        precipitation_display = "강수없음" if precipitation_of_today == 0 else f"{precipitation_of_today}"
        
        # 메시지 제목 설정
        header = f"*『{cluster.name}』* *{date_of_today} 날씨 : {weather_of_today}*\n\n"
            
        weather_msg = (
            f"🥶  *최저 기온* : {lowest_temp_of_today}°C\n"
            f"🥵  *최고 기온* : {highest_temp_of_today}°C\n"
            f"☔️  *강 수* : {'0mm' if precipitation_of_today == 0 else precipitation_of_today}"
            f"  (습도 : {humidity_of_today}%)\n"
            f"❄  *강 설* : {'0cm' if snowfall_of_today == 0 else snowfall_of_today}"
            f"🌪  *풍 속* : {weendspeed_of_today}m/s\n"
        )

        if float(perceived_temp) > 33.0 and precipitation_of_today == 0:
            weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n환절기에는 면역력이 떨어지기 쉽습니다! *규칙적인 운동!* 💪, *충분한 휴식!* 🛌 으로 건강을 지키세요!\n\n언제나 임직원분들의 건강을 응원합니다.\n감사합니다."
            
        if float(perceived_temp) < 10.0 and precipitation_of_today == 0:
            weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n겨울이 찾아와 기온이 뚝 떨어졌습니다! *따뜻한 물!* 🍵, *따뜻한 옷!* 🧣, *규칙적인 운동!* 💪 을 통해 건강관리에 유의하여 주시기 바랍니다.\n\n언제나 임직원분들의 건강을 응원합니다.\n감사합니다."

        # 폭염특보 안전멘트
        if float(perceived_temp) >= 33.0 and precipitation_of_today == 0:
            if cluster.name == '김포 클러스터':
                weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 🌞 *폭염특보* 🌞가 발효되었습니다.\n\n✔ 임직원 여러분들께서는 아래의 사항 체크해주세요!\n       1. 작업 전 : 동료간 건강상태 이상 유무 체크\n       2. 작업 중 : 안색창백, 동공풀림, 기력저하 등 온열질환 증상 발현 시\n                          관리감독자 즉시 보고 → EHS팀(☎ 010-5820-4261) 즉시 보고\n\n✔ 온열질환 예방 3대수칙! 시원한 *물!* 🧊, *그늘!* 🏖, *휴식!* 🛌\n\n감사합니다."
            elif cluster.name == '평택 클러스터':
                weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 🌞 *폭염특보* 🌞가 발효되었습니다.\n\n✔ 임직원 여러분들께서는 아래의 사항 체크해주세요!\n       1. 작업 전 : 동료간 건강상태 이상 유무 체크\n       2. 작업 중 : 안색창백, 동공풀림, 기력저하 등 온열질환 증상 발현 시\n                          관리감독자 즉시 보고 → EHS팀(☎ 010-5820-4327) 즉시 보고\n\n✔ 온열질환 예방 3대수칙! 시원한 *물!* 🧊, *그늘!* 🏖, *휴식!* 🛌\n\n감사합니다."
            elif cluster.name == '창원 클러스터':
                weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 🌞 *폭염특보* 🌞가 발효되었습니다.\n\n✔ 임직원 여러분들께서는 아래의 사항 체크해주세요!\n       1. 작업 전 : 동료간 건강상태 이상 유무 체크\n       2. 작업 중 : 안색창백, 동공풀림, 기력저하 등 온열질환 증상 발현 시\n                          관리감독자 즉시 보고 → EHS팀(☎ 010-5820-7439) 즉시 보고\n\n✔ 온열질환 예방 3대수칙! 시원한 *물!* 🧊, *그늘!* 🏖, *휴식!* 🛌\n\n감사합니다."
        
        # 강수 안전멘트
        if float(perceived_temp) >= 33.0 and precipitation_of_today != 0:
            weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 ☔️ 비 소식이 있습니다.\n사업장 내 이동 및 작업 시 미끄러짐 위험이 있으니, 🚷 뛰지 마시고, 🚶‍♀️ 천천히 이동하여 주시기 바랍니다.\n감사합니다."
        
        if float(perceived_temp) < 33.0 and precipitation_of_today != 0:
            weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 ☔️ 비 소식이 있습니다.\n사업장 내 이동 및 작업 시 미끄러짐 위험이 있으니, 🚷 뛰지 마시고, 🚶‍♀️ 천천히 이동하여 주시기 바랍니다.\n감사합니다."

        # 강설 안전멘트
        if float(perceived_temp) < 10.0 and snowfall_of_today != 0:
            weather_msg += "\n\n안녕하세요!\n컬리 EHS 팀 입니다.\n\n금일 ❄ 눈 소식이 있습니다.\n겨울철 미끄럼 사고 위험이 높으니, 사업장 내 이동 및 작업 시 🚷 뛰지 마시고 🚶‍♀️ 천천히 이동하여 주시기 바라며,\n*따뜻한 물!* 🍵, *따뜻한 옷!* 🧣, *규칙적인 운동!* 💪 을 통해 건강관리에 유의하여 주시기 바랍니다.\n감사합니다."    
        
        # 메시지 본문
        body = header + weather_msg
    
        # 슬랙 채널에 전송
        send_slack_message(body, cluster.channel)

if __name__ == "__main__":
    main()
