import datetime
import json
import sys
from urllib import request, parse
from http.client import HTTPResponse
import subprocess

def sunrise_sunset_get(lat_value: str, lon_value: str) -> tuple[dict, bool]:
    """Получение данных о восходе и закате солнца."""
    base_url = "https://api.sunrise-sunset.org/json"
    query_params = parse.urlencode({
        "lat": lat_value,
        "lng": lon_value,
        "date": "today",
        "formatted": 0
    })
    url = f"{base_url}?{query_params}"
    
    try:
        with request.urlopen(url) as response:
            if response.status == 200:
                data = json.load(response)
                return data, True
            else:
                return {}, False
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}, False

def publish_message(topic: str, message: str) -> None:
    """Публикация сообщений в MQTT через subprocess."""
    subprocess.run(["mosquitto_pub", "-h", "127.0.0.1", "-t", topic, "-m", message], check=True)

def sunrise_sunset_processing(lat_value: str, lon_value: str) -> None:
    """Обработка данных о восходе и закате солнца."""
    raw_data, req_status = sunrise_sunset_get(lat_value, lon_value)
    if req_status:
        try:
            sunrise = raw_data["results"]["sunrise"]
            sunset = raw_data["results"]["sunset"]
            
            # Публикация через MQTT
            publish_message("local_python/sunset_sunrise/sunrise", sunrise)
            publish_message("local_python/sunset_sunrise/sunset", sunset)
            publish_message("local_python/weather/StatusAstronomicalDataDownload", "success")
        except KeyError as e:
            print(f"Error processing data: {e}")
            publish_message("local_python/weather/StatusAstronomicalDataDownload", "error")
    else:
        publish_message("local_python/weather/StatusAstronomicalDataDownload", "error")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <latitude> <longitude>")
        sys.exit(1)
    
    latitude = sys.argv[1]
    longitude = sys.argv[2]
    sunrise_sunset_processing(latitude, longitude)
