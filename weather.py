from datetime import datetime, timedelta
import logging
import time


from homeassistant.components.weather import (
    WeatherEntity, ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING, ATTR_FORECAST_WIND_SPEED)

from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    CONF_CODE,
    CONF_NAME,
    CONF_SCAN_INTERVAL
)

import requests
import json

_LOGGER = logging.getLogger(__name__)

VERSION = '1.0.0'
DOMAIN = 'weathernmc'

CONDITION_MAP = {
    '晴': 'sunny',
    '多云': 'cloudy',
    '局部多云': 'partlycloudy',
    '阴': 'cloudy',
    '雾': 'fog',
    '中雾': 'fog',
    '大雾': 'fog',
    '小雨': 'rainy',
    '中雨': 'rainy',
    '大雨': 'pouring',
    '暴雨': 'pouring',
    '雾': 'fog',
    '小雪': 'snowy',
    '中雪': 'snowy',
    '大雪': 'snowy',
    '暴雪': 'snowy',
    '扬沙': 'fog',
    '沙尘': 'fog',
    '雷阵雨': 'lightning-rainy',
    '冰雹': 'hail',
    '雨夹雪': 'snowy-rainy',
    '大风': 'windy',
    '薄雾': 'fog',
    '雨': 'rainy',
    '雪': 'snowy',
    '9999': 'exceptional',
    
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities(
        [
            NMCWeather(
                code=config.get(CONF_CODE),
                name=config.get(CONF_NAME, 'weathernmc'),
                interval=config.get(CONF_SCAN_INTERVAL, 60)
            )
        ]
    )


class NMCWeather(WeatherEntity):

    def __init__(self, code: str, name: str, interval: int):
        self.code = code
        self._name = name
        self.interval = interval
        self.update_ts = int(time.time())
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        skycon = self.weather_data['real']['weather']['info']
        return CONDITION_MAP[skycon]

    @property
    def temperature(self):
        return self.weather_data['real']['weather']['temperature']

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def humidity(self):
        return float(self.weather_data['real']['weather']['humidity']) 

    @property
    def wind_speed(self):
        return self.weather_data['real']['wind']['speed']

    @property
    def wind_bearing(self):
        return self.weather_data['real']['wind']['direct']

    @property
    def wind_speed(self):
        return self.weather_data['real']['wind']['power']


    @property
    def pressure(self):
        return round(float(self.weather_data['real']['weather']['airpressure']) / 100, 2)


    @property
    def attribution(self):
        return 'Powered by WWW.NMC.COM'

    @property
    def aqi(self):
        return self.weather_data['air']['aqi']

    @property
    def aqi_description(self):
        return self.weather_data['air']['aqi']
        
    @property
    def alert(self):
        return self.weather_data['real']['warn']['alert']

    @property
    def state_attributes(self):
        data = super(NMCWeather, self).state_attributes
        data['aqi'] = self.aqi 
        return data  

    @property
    def forecast(self):
        forecast_data = []
        for i in range(1, 7):
            time_str = self.weather_data['predict']['detail'][i]['date']
            data_dict = {
                ATTR_FORECAST_TIME: datetime.strptime(time_str, '%Y-%m-%d'),
                ATTR_FORECAST_CONDITION: CONDITION_MAP[self.weather_data['predict']['detail'][i]['day']['weather']['info']],
                ATTR_FORECAST_TEMP: self.weather_data['tempchart'][i+7]['max_temp'],
                ATTR_FORECAST_TEMP_LOW: self.weather_data['tempchart'][i+7]['min_temp'],
                ATTR_FORECAST_WIND_BEARING: self.weather_data['predict']['detail'][i]['day']['wind']['direct'],
                ATTR_FORECAST_WIND_SPEED: self.weather_data['predict']['detail'][i]['day']['wind']['power']
            }
            forecast_data.append(data_dict)

        return forecast_data

    def update(self):
        now_ts = int(time.time())
        # print(self.interval)
        if now_ts < self.update_ts + int(self.interval):
            _LOGGER.warning('WeatherNMC waring: update too fast;')
            return
            # time.sleep(self.interval)
            # time.sleep(10)
        weather_uri = 'http://www.nmc.cn/rest/weather?stationid=%s' % self.code
        try:
            self._weather_data = requests.get(weather_uri, timeout=3).json()
            self.weather_data = self._weather_data['data']
            
            # _LOGGER.warning(self.weather_data)
            self.update_ts = int(time.time())
        except Exception as e:
            # print(weather_uri)
            # print(self.weather_data)
            _LOGGER.warning('WeatherNMC waring: %s' % e)
            time.sleep(10)
            self.update()
            
