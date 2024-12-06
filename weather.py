import datetime
import json
import sys
from urllib import request, parse
from http.client import HTTPResponse
from subprocess import run

def weather_get(access_key: str, lat_value: str, lon_value: str) -> tuple[dict, bool]:
    headers = {
        "X-Yandex-Weather-Key": access_key
    }
    query = {
        "query": f"""
        {{
         weatherByPoint(request: {{ lat: {lat_value}, lon: {lon_value} }}) {{
           now {{
             temperature
             feelsLike
             windSpeed
             condition
           }}
         }}
        }}
        """
    }
    url = "https://api.weather.yandex.ru/graphql/query"
    data = json.dumps(query).encode("utf-8")
    
    req = request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with request.urlopen(req) as response:
            if response.status == 200:
                return json.load(response), True
            else:
                return {}, False
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {}, False

def publish_message(topic: str, message: str) -> None:
    run(["mosquitto_pub", "-h", "127.0.0.1", "-t", topic, "-m", message], check=True)

def weather_processing(access_key: str, lat_value: str, lon_value: str) -> None:
    raw_weather, req_status = weather_get(access_key, lat_value, lon_value)
    if req_status:
        try:
            weather_data = raw_weather["data"]["weatherByPoint"]["now"]
            temperature = weather_data["temperature"]
            feels_like = weather_data["feelsLike"]
            wind_speed = weather_data["windSpeed"]
            condition = weather_data["condition"]
            data_update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            publish_message("local_python/weather/temperature", str(temperature))
            publish_message("local_python/weather/feelsLike", str(feels_like))
            publish_message("local_python/weather/windSpeed", str(wind_speed))
            publish_message("local_python/weather/condition", str(condition))
            publish_message("local_python/weather/DataUpdTime", f'"{data_update_time}"')
            publish_message("local_python/weather/StatusWeatherDataDownload", "success")
        except KeyError as e:
            print(f"Error processing weather data: {e}")
            publish_message("local_python/weather/StatusWeatherDataDownload", "error")
    else:
        publish_message("local_python/weather/StatusWeatherDataDownload", "error")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <access_key> <latitude> <longitude>")
        sys.exit(1)

    access_key_1 = sys.argv[1]
    latitude = sys.argv[2]
    longitude = sys.argv[3]
    weather_processing(access_key_1, latitude, longitude)
