import datetime
import requests
import json
import os
import sys

def sunriseSunsetGet(lat_value,lon_value):
    status = False
    url = "https://api.sunrise-sunset.org/json?lat=" + lat_value + "&lng=" + lon_value + "&date=today&formatted=0"
    response = requests.get(url)
    if response.ok:
        status = True
    else:
        status = False
    return response.content,status

def sunriseSunsetProcessing(lat_value,lon_value):
    current_time = datetime.datetime.now()
    raw_data, req_status = sunriseSunsetGet(lat_value,lon_value)
    if req_status:
        sunriseSunsetdata = json.loads(raw_data.decode('utf-8'))
        print(sunriseSunsetdata)
        sunrise = sunriseSunsetdata["results"]["sunrise"]
        sunset = sunriseSunsetdata["results"]["sunset"]
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/sunset_sunrise/sunrise -m ' +  sunrise)
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/sunset_sunrise/sunset -m ' +  sunset)
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/StatusAstronomicalDataDownload -m ' + 'success')
    else:
        os.system('mosquitto_pub -h 127.0.0.1 -t local_python/weather/StatusAstronomicalDataDownload -m ' + 'error')

if __name__ == '__main__':
    latitude = str(sys.argv[1])
    longitude = str(sys.argv[2])
    sunriseSunsetProcessing(latitude,longitude)
