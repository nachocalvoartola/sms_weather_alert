import os
from twilio.rest import Client
from twilio_config import PHONE_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, API_KEY_WAPI
import time

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from datetime import datetime

#Auxiliar function to get weather variables by hour

def get_forecast(response, i):
    date = response['forecast']['forecastday'][0]['date']
    hour = int (response['forecast']['forecastday'][0]['hour'][i]['time'].split(' ')[1].split(':')[0])
    condition = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temperature = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    rain_probability = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    return date, hour, condition, temperature, rain, rain_probability 

#Alert filters
temp_max = 32
temp_min = 5
rain = 1
rain_prob = 60


#URL parameters

city = 'madrid'
api_key = API_KEY_WAPI
days = '2'
air_quality = 'yes'
weather_alert = 'no'
url_weather = 'http://api.weatherapi.com/v1/forecast.json?key=' + api_key + '&q=' + city + '&days=' + days + '&aqi=' + air_quality + '&alerts=' + weather_alert

#URL request

response = requests.get(url_weather).json()

#Dataframe creation

data = []

for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour = 'red'):
    data.append(get_forecast(response, i))

col = ['date', 'hour', 'condition', 'temp', 'rain', 'rain_prob']

df = pd.DataFrame(data, columns=col)

df_filter = df[(df['temp'] >= temp_max) | (df['temp'] <= temp_min) | (df['rain'] == rain) | (df['rain_prob'] >= rain_prob)]

#SMS send

text = '\nAlert for temperatures above ' + str (temp_max) + ' in ' + city + ': \n\n ' + str (df_filter[['hour', 'temp']].set_index('hour'))

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

message = client.messages.create(  
  body = text,
  from_ = PHONE_NUMBER,
  to='+34658936280'
)

print('Mensaje enviado ' + message.sid)




