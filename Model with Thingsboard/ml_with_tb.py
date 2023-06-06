import os
import time
import sys
import json
import random
import paho.mqtt.client as mqtt
from threading import Thread
import pickle
from river import metrics
import pandas as pd

# initialising metrics
metric = metrics.Accuracy()
metric1 = metrics.Accuracy()
metric2 = metrics.Accuracy()

# Assigning models
# model = pickle.load(open('trained_ADA_HTC_full.pkl', 'rb'))
# model_HWT = pickle.load(open('trained_ADA_HTC_HWT.pkl', 'rb'))
# model2_LTC = pickle.load(open('trained_ADA_HTC_LTC.pkl', 'rb'))

# Thingsboard platform credentials
THINGSBOARD_HOST = 'demo.thingsboard.io'        # Change IP Address
ACCESS_TOKEN = 'ziad1234'                      # Change Access Token
# initial data
sensor_data = {
    "temperature1": 0,
    "temperature2": 0,
    "light1": 0,
    "light2": 0,
    "humidity1": 0,
    "humidity2": 0,
    "weekday": 0,
    "time": 0,
    "pir": 0,
    "led": 0,
    "accuracy": 0
    }

def publishValue(client):
    INTERVAL = 1
    print("Thread  Started")
    next_reading = time.time()
    while True:
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data),1)
        next_reading += INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

def read_sensor():    
    # assigning reading
    temp = sensor_data['temperature']
    light = sensor_data['light']
    co2 = sensor_data['co2']
    humidity = sensor_data['humidity']
    weekday = sensor_data['weekday']
    time = sensor_data['time']
    pir = sensor_data['pir']
    led = sensor_data["led"]
    accuracy = sensor_data["accuracy"]
    
    print("Temperature read : ",temp,"C")
    print("light read : ",light)
    print("co2 read : ",co2)
    print("humidity read : ",humidity)
    print("weekday read : ",weekday)
    print("time read : ",time)
    print("pir read : ",pir)
    print("led read : ",led)
    print("accuracy read : ",accuracy)
    
    return temp, light, co2, humidity, weekday, time, pir, led, accuracy

# Function will set the temperature value in device
def setTemp (params):
    sensor_data['temperature'] = params
    #print("Rx setValue is : ",sensor_data)
    print("Temperature Set : ",params,"C")
# Function will set the light value in device
def setLight (params):
    sensor_data['led'] = params
    #print("Rx setValue is : ",sensor_data)
    print("Light Set : ",params)

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    #print("rc code:", rc)
    client.subscribe('v1/devices/me/rpc/request/+')

# MQTT on_message callback function
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    if msg.topic.startswith('v1/devices/me/rpc/request/'):
        requestId = msg.topic[len('v1/devices/me/rpc/request/'):len(msg.topic)]
        # print("requestId : ", requestId)
        data = json.loads(msg.payload)
        
        # ----------------- "Get" Method Handling -----------------
        if data['method'] == 'getTemp':
            #print("getvalue request\n")
            #print("sent getValue : ", sensor_data)
            client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['temperature']), 1)
        if data['method'] == 'getLight':
            #print("getvalue request\n")
            #print("sent getValue : ", sensor_data)
            client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['light']), 1)
            
        # ----------------- "Set" Method Handling -----------------
        if data['method'] == 'setTemp':
            #print("setvalue request\n")
            params = data['params']
            # print(f"Temp: Data is {data}\nParams are: {params}")
            setTemp(params)
        if data['method'] == 'setLight':
            #print("setvalue request\n")
            params = data['params']
            # print(f"Light: Data is {data}\nParams are: {params}")
            setLight(params)

# create a client instance
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST,1883,60)

t = Thread(target=publishValue, args=(client,))


try:
    client.loop_start()
    t.start()
    while True:
        # Dummy data
        light_data = round(random.uniform(0, 2400), 2)
        temp_data = round(random.uniform(20, 30), 2)
        co2_data = round(random.uniform(62, 1200), 2)
        hum_data = round(random.uniform(42, 72), 2)
        weekday_data = random.randint(0, 6)
        time_data = random.randint(0, 23)
        
        # new Sensor values
        x = {"light": light_data,
             'temperature': temp_data,
             "co2": co2_data,
             "humidity": hum_data,
             "weekday": weekday_data,
             "time": time_data}
        
        x = {k: v for k, v in x.items() if v is not None}
        
        # ----------------- ML Model Fusion -----------------
        if (len(x) == 6):
            # model prediction
            pir_data = model.predict_one(x)
            model.learn_one(x, pir_data)
            z = model.predict_one(x)
            accuracy = metric.update(pir_data, z)
            # print(f"the pred is {pir_data}")
        elif ((len(x) == 3) and (("temperature" and "light" and "co2") in x)):
            # model prediction
            pir_data = model2_LTC.predict_one(x)
            model2_LTC.learn_one(x, pir_data)
            z = model2_LTC.predict_one(x)
            accuracy = metric1.update(pir_data, z)
            # print(f"the pred is {pir_data}")
        elif ((len(x) == 3) and (("humidity" and "weekday" and "time") in x)):
            # model prediction
            pir_data = model_HWT.predict_one(x)
            model_HWT.learn_one(x, pir_data)
            z = model_HWT.predict_one(x)
            accuracy = metric2.update(pir_data, z)
            # print(f"the pred is {pir_data}")
        
        sensor_data = {**sensor_data,
                       **x,
                       "pir": int(pir_data),
                       "accuracy": str(accuracy).split(" ")[1]}
        # sensor_data = {**sensor_data,
        #                "light": light_data,
        #                'temperature': temp_data,
        #                "co2": co2_data,
        #                "humidity": hum_data,
        #                "weekday": weekday_data,
        #                "time": time_data,
        #                "pir": int(pir_data),
        #                "accuracy": str(accuracy).split(" ")[1]}

except KeyboardInterrupt:
    client.disconnect()


