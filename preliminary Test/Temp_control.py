import os
import time
import sys
import json
import random
import paho.mqtt.client as mqtt
from threading import Thread
import serial

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    ser.flush()

# Thingsboard platform credentials
THINGSBOARD_HOST = 'demo.thingsboard.io'  # Change IP Address
ACCESS_TOKEN = 'ziadrpc'
#sensor_data = {'temperature': 25}
sensor_data = {'temperature': 0, "settemp": None}


def publishValue(client):
    INTERVAL = 1
    print("Thread  Started")
    next_reading = time.time()
    while True:
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
        next_reading += INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)


def read_temperature():
    temp = sensor_data['temperature']
    return temp

# Function will set the temperature value in device
def setValue(params):
    params = int(params)
    print("Temperature Set : ", params, "C")
    sensor_data['settemp'] = params
    # print("Rx setValue is : ",sensor_data)

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    #print("rc code:", rc)
    client.subscribe('v1/devices/me/rpc/request/+')

# MQTT on_message callback function
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    if msg.topic.startswith('v1/devices/me/rpc/request/'):
        requestId = msg.topic[len('v1/devices/me/rpc/request/'):len(msg.topic)]
        #print("requestId : ", requestId)
        data = json.loads(msg.payload)
    if data['method'] == 'getValue':
        #print("getvalue request\n")
        #print("sent getValue : ", sensor_data)
        read_temperature()
        client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['temperature']), 1)
    if data['method'] == 'setValue':
        #print("setvalue request\n")
        params = data['params']
        setValue(float(params))

# create a client instance
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

t = Thread(target=publishValue, args=(client,))

try:
    client.loop_start()
    t.start()
    while True:
        if ser.in_waiting > 0:
            sensor_data["temperature"] = ser.readline().decode("utf-8").rstrip()
            print("Sensor Data: " + sensor_data["temperature"])
        if float(sensor_data["temperature"]) <= 20:
            ser.write(b"blue\n")
            #print("LED: Blue")
        elif float(sensor_data["temperature"]) > 20 and float(sensor_data["temperature"]) <= 25:
            ser.write(b"green\n")
            #print("LED: Green")
        elif float(sensor_data["temperature"]) > 25 and float(sensor_data["temperature"]) <= 30:
            ser.write(b"yellow\n")
            #print("LED: Yellow")
        elif float(sensor_data["temperature"]) > 30:
            ser.write(b"red\n")
            #print("LED: Red")
        else:
            ser.write(b"all\n")
            #print("LED: All")
except KeyboardInterrupt:
    client.disconnect()
