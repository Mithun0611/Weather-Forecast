import requests
import json

API_KEY = "0ff7d925fe0cdc9e698c7d9f8e78cfdd"

def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        times, temps = [], []
        for item in data["list"]:
            times.append(item["dt_txt"])
            temps.append(item["main"]["temp"])
        return {"times": times, "temps": temps}
    return None
