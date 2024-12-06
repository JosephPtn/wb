import datetime
import requests
import json
import os
import sys

access_key_1 = " "

def weatherGet(access_key,lat_value,lon_value):
    status = False
    headers = {
        "X-Yandex-Weather-Key": access_key
    }
    query = """{
     weatherByPoint(request: { lat: %s, lon: %s }) {
       now {
         temperature
         feelsLike
         windSpeed
         condition
       }
     }
    }""" % (lat_value,lon_value)
    response = requests.post('https://api.weather.yandex.ru/graphql/query', headers=headers, json={'query': query})
    if response.ok:
        status = True
    else:
        status = False
    return response.content,status
  
def weatherProcessing(access_key,lat_value,lon_value):
    current_time = datetime.datetime.now()
    raw_weather, req_status = weatherGet(access_key,lat_value,lon_value)
    if req_status:
        weather_data = json.loads(raw_weather.decode('utf-8'))
        temperature = weather_data["data"]["weatherByPoint"]["now"]["temperature"]
        feelsLike = weather_data["data"]["weatherByPoint"]["now"]["feelsLike"]
        windSpeed = weather_data["data"]["weatherByPoint"]["now"]["windSpeed"]
        condition = weather_data["data"]["weatherByPoint"]["now"]["condition"]
        DataUpdateTime = str(current_time.strftime('%Y-%m-%d %H:%M:%S'))
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/temperature -m ' + str(temperature))
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/feelsLike -m ' + str(feelsLike))
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/windSpeed -m ' + str(windSpeed))
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/condition -m ' + str(condition))
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/DataUpdTime -m ' + '"' + DataUpdateTime + '"')
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/StatusWeatherDataDownload -m ' + 'success')
    else:
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/StatusWeatherDataDownload -m ' + 'error')
      
if __name__ == '__main__':
    access_key_1 = str(sys.argv[1])
    latitude = str(sys.argv[2])
    longitude = str(sys.argv[3])
    weatherProcessing(access_key_1,latitude,longitude)
