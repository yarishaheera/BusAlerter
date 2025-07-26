import os
from datetime import datetime

import requests
import pytz

# Load from environment
TELEGRAM_TOKEN = os.getenv("TEL_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
LTA_API_KEY = os.getenv("LTA_KEY", "")
MORNING_BUS_STOP_CODE = "14339"
EVENING_BUS_STOP_CODE = "05419"
MORNING_BUS = "124"
EVENING_BUS = "145"

# Timezone
SG_TIMEZONE = pytz.timezone('Asia/Singapore')
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

def get_bus_arrivals(current_time, bus_stop_code, bus_number):
    headers = {"AccountKey": LTA_API_KEY}
    params = {"BusStopCode": bus_stop_code, "ServiceNo": bus_number}
    url = f"https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        message = ""
        service = data['Services'][0]
        est = service["NextBus"]["EstimatedArrival"]
        est_formatted = datetime.strptime(est, DATETIME_FORMAT)
        time_left = int(((est_formatted - current_time).total_seconds()) // 60)
        if time_left <= 0:
            message += f"🚌 *Bus {bus_number}: Arriving soon*\n"
        elif time_left <= 10:
            message += f"🚌 *Bus {bus_number} arriving in {time_left} min*\n"
        return message
    except Exception as e:
        return f"Error fetching bus arrivals: {e}"


def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print("an exception occurred when sending the message: ", e)



if __name__ == "__main__":
    current_time = datetime.now(SG_TIMEZONE)
    today_morning_start = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    today_morning_end = current_time.replace(hour=10, minute=0, second=0, microsecond=0)

    today_evening_start = current_time.replace(hour=14, minute=0, second=0, microsecond=0)
    today_evening_end = current_time.replace(hour=15, minute=0, second=0, microsecond=0)



    bus_msg = ""
    if today_morning_start <= current_time <= today_morning_end:
        bus_msg = get_bus_arrivals(current_time, MORNING_BUS_STOP_CODE, MORNING_BUS)
    elif today_evening_start <= current_time <= today_evening_end:
        bus_msg = get_bus_arrivals(current_time, EVENING_BUS_STOP_CODE, EVENING_BUS)

    if bus_msg != "":
        send_telegram_message(bus_msg)
