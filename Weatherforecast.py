import os
import requests


def get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少環境變數：{name}")
    return value


def get_rain_probability(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_probability_max",
        "timezone": "Asia/Taipei",
        "forecast_days": 1,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    probability = data["daily"]["precipitation_probability_max"][0]
    date = data["daily"]["time"][0]

    if probability is None:
        raise RuntimeError("Open-Meteo 沒有提供今日降雨機率")

    return date, probability


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=20,
    )

    response.raise_for_status()


def main():

    # 非敏感資料放 GitHub Variables
    latitude = get_required_env("WEATHER_LAT")
    longitude = get_required_env("WEATHER_LON")

    threshold = int(os.getenv("RAIN_THRESHOLD") or "70")

    # 敏感資料由 GitHub Secrets 傳入
    telegram_token = get_required_env("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = get_required_env("TELEGRAM_CHAT_ID")

    # 手動測試時可以強制通知
    force_notify = (
        os.getenv("FORCE_NOTIFY", "false").lower() == "true"
    )

    date, rain_probability = get_rain_probability(
        latitude,
        longitude
    )

    print(f"日期：{date}")
    print(f"今日最高降雨機率：{rain_probability}%")
    print(f"通知門檻：{threshold}%")

    if rain_probability > threshold or force_notify:

        if force_notify:
            message = (
                f"🧪 雨天通知測試\n\n"
                f"📅 {date}\n"
                f"☔ 今日最高降雨機率：{rain_probability}%\n\n"
                f"記得帶傘喔！"
            )
        else:
            message = (
                f"☔ 雨天提醒\n\n"
                f"📅 {date}\n"
                f"🌧 今日最高降雨機率：{rain_probability}%\n\n"
                f"降雨機率超過 {threshold}%\n"
                f"記得帶傘喔！"
            )

        send_telegram_message(
            telegram_token,
            telegram_chat_id,
            message
        )

        print("Telegram 通知已發送。")

    else:
        print("降雨機率未超過門檻，不發送通知。")


if __name__ == "__main__":
    main()
