
//Виртуальное устройство weather на WB
defineVirtualDevice("weather", {
    title: "Weather",
	cells: {
        latitude: {
        	type: "text",
            value : " ",
            readonly: false,
            title: {
              "en": "Geographical latitude",
              "ru": "Географическая широта",
                   },
        },
        longitude: {
        	type: "text",
            value : " ",
            readonly: false,
            title: {
              "en": "Geographical longitude",
              "ru": "Географическая долгота",
                   },
        },
        YandexWeatherApiKey: {
        	type: "text",
            value : " ",
            readonly: false,
            title: {
              "en": "Yandex Weather API Key",
              "ru": "Ключ API Яндекс Погоды",
                   },
        },
      	temperature: {
        	type: 'value',
            units: 'deg C',
            value: 0.0,
            readonly: true,
            title: {
              "en": "Temperature",
              "ru": "Температура",
                   },
        },
        feelsLike: {
            type: 'value',
            units: 'deg C',
            value: 0.0,
            readonly: true,
            title: {
              "en": "It feels like",
              "ru": "Ощущается как",
                   },
        },
        windSpeed: {
            type: 'value',
            units: 'm/s',
            value: 0.0,
            readonly: true,
            title: {
              "en": "Wind speed at a height of 10 meters from the earth's surface",
              "ru": "Скорость ветра на высоте 10 метров от поверхности земли",
                   },
        },
        condition: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "General weather conditions",
              "ru": "Общие погодные условия",
                   },
        },
        DataUpdateTime: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Data loading time",
              "ru": "Время загрузки данных",
                   },
        },
        sunrise: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Sunrise",
              "ru": "Восход солнца",
                   },
        },
        sunset: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Sunset",
              "ru": "Закат",
                   },
        },
        UploadingDataSwitch : {
        	type : "switch",
			value : false,
            readonly: false,
            title: {
              "en": "Uploading data",
              "ru": "Загрузка данных",
                   },
        },
        sunset: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Sunset",
              "ru": "Закат",
                   },
        },
        StatusWeatherDataDownload: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Status of the weather data download",
              "ru": "Статус загрузки погодных данных",
                   },
        },
        StatusAstronomicalDataDownload: {
            type: "text",
            value : " ",
            readonly: true,
            title: {
              "en": "Status of astronomical data download",
              "ru": "Статус загрузки астрономических данных",
                   },
        },
        
	}
});

// запрос астрономических данных один раз в 03:05
defineRule("cronSunset_Sunrise", {
  // https://pkg.go.dev/github.com/robfig/cron#hdr-CRON_Expression_Format
  when: cron("0 05 03 * * *"),
  then: function () {
    if (dev["weather"]["UploadingDataSwitch"] > 0) {
      var latitude = dev["weather"]["latitude"];
      var longitude = dev["weather"]["longitude"];
      var Command = 'python3 /root/script/python/sunset_sunrise.py "{}" "{}"'.format(latitude,longitude);
      runShellCommand(Command);
    }
  }
});

// запрос погодных данных один раз в час
defineRule("cronWeather", {
  // https://pkg.go.dev/github.com/robfig/cron#hdr-CRON_Expression_Format
  when: cron("0 0 * * * *"),
  then: function () {
    if (dev["weather"]["UploadingDataSwitch"] > 0) {
      var key = dev["weather"]["YandexWeatherApiKey"];
      var latitude = dev["weather"]["latitude"];
      var longitude = dev["weather"]["longitude"];
      var Command = 'python3 /root/script/python/weather.py "{}" "{}" "{}"'.format(key,latitude,longitude);
      runShellCommand(Command);
    }
  }
});

// StatusWeatherDataDownload
trackMqtt("local_python/weather/StatusWeatherDataDownload", function(msg){
  dev["weather"]["StatusWeatherDataDownload"] = msg.value;
});

// StatusAstronomicalDataDownload
trackMqtt("local_python/weather/StatusAstronomicalDataDownload", function(msg){
  dev["weather"]["StatusAstronomicalDataDownload"] = msg.value;
});

// temperature
trackMqtt("local_python/weather/temperature", function(msg){
  dev["weather"]["temperature"] = parseFloat(msg.value);
});

// feelsLike
trackMqtt("local_python/weather/feelsLike", function(msg){
  dev["weather"]["feelsLike"] = parseFloat(msg.value);
});

// windSpeed
trackMqtt("local_python/weather/windSpeed", function(msg){
  dev["weather"]["windSpeed"] = parseFloat(msg.value);
});

// condition
trackMqtt("local_python/weather/condition", function(msg){
  dev["weather"]["condition"] = msg.value;
});

// DataUpdateTime
trackMqtt("local_python/weather/DataUpdTime", function(msg){
  dev["weather"]["DataUpdateTime"] = msg.value;
});

// sunset
trackMqtt("local_python/sunset_sunrise/sunset", function(msg){
  var raw_sunset_utc = msg.value;
  var sunset_utc = new Date(raw_sunset_utc);
  var sunset_msk = sunset_utc.toLocaleString(undefined, { timeZone: 'Europe/Moscow' });
  dev["weather"]["sunset"] = sunset_msk;
});

// sunrise
trackMqtt("local_python/sunset_sunrise/sunrise", function(msg){
  var raw_sunrise_utc = msg.value;
  var sunrise_utc = new Date(raw_sunrise_utc);
  var sunrise_msk = sunrise_utc.toLocaleString(undefined, { timeZone: 'Europe/Moscow' });
  dev["weather"]["sunrise"] = sunrise_msk;
});

//Правило для проверки корректности настроек для загрузки данных
defineRule("CheckingSettings", {
	whenChanged:"weather/UploadingDataSwitch",
	then: function (newValue, devName, cellName) {
        if (newValue > 0) {
          if (dev["weather"]["latitude"] == null || dev["weather"]["longitude"] == null || dev["weather"]["YandexWeatherApiKey"] == null ) {
            dev["weather"]["UploadingDataSwitch"] = false
          }
        }
	}      
});
