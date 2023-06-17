import os
import time
import datetime
import sys
import json
import random
import paho.mqtt.client as mqtt
from threading import Thread
import pickle
from river import metrics
import pandas as pd
import serial

fan_state = False
led_state = False

if __name__ == "__main__":
    # ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
    ser = serial.Serial("COM8", 9600, timeout = 1)
    # ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
    ser.flush()

# initialising metrics
# Light model
metric1_L = metrics.Accuracy()
metric2_L = metrics.Accuracy()
metric3_L = metrics.Accuracy()

# Temp model
metric1_T = metrics.Accuracy()
metric2_T = metrics.Accuracy()
metric3_T = metrics.Accuracy()

# Assigning models
# Light model
model_L = pickle.load(open('trained_ADA_AFC_light.pkl', 'rb'))
model1_L_5 = pickle.load(open('trained_ADA_AFC_light.pkl', 'rb'))
model2_L_5 = pickle.load(open('trained_ADA_AFC_light.pkl', 'rb'))

# Temp model
model_T = pickle.load(open('trained_ADA_AFC_temp.pkl', 'rb'))
model1_T_5 = pickle.load(open('trained_ADA_AFC_temp.pkl', 'rb'))
model2_T_5 = pickle.load(open('trained_ADA_AFC_temp.pkl', 'rb'))

# Thingsboard platform credentials
THINGSBOARD_HOST = 'demo.thingsboard.io'        # Change IP Address
ACCESS_TOKEN = 'ziad12345'                      # Change Access Token
# initial data
sensor_data = {
    "Temperature1": 0,
    "Temperature2": 0,
    "LDR1": 0,
    "LDR2": 0,
    "Humidity1": 0,
    "Humidity2": 0,
    "weekday": 0,
    "time": 0,
    "PIR_value": 0,
    "led": False,
    "Manual_light": False,
    "fan": False,
    'Manual_fan': False,
    "light accuracy": 0,
    "temp accuracy": 0,
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
    temp1 = sensor_data['Temperature1']
    temp2 = sensor_data['Temperature2']
    light1 = sensor_data['LDR1']
    light2 = sensor_data['LDR2']
    humidity1 = sensor_data['Humidity1']
    humidity2 = sensor_data['Humidity2']
    weekday = sensor_data['weekday']
    time = sensor_data['time']
    pir = sensor_data['PIR_value']
    led = sensor_data["led"]
    light_accuracy = sensor_data["light accuracy"]
    temp_accuracy = sensor_data["temp accuracy"]
    
    print("Temperature1 read : ",temp1,"C")
    print("Temperature2 read : ",temp2,"C")
    print("light1 read : ",light1)
    print("light2 read : ",light2)
    print("humidity1 read : ",humidity1)
    print("humidity2 read : ",humidity2)
    print("weekday read : ",weekday)
    print("time read : ",time)
    print("pir read : ",pir)
    print("led read : ",led)
    print("Light accuracy read : ",light_accuracy)
    print("Temp accuracy read : ",temp_accuracy)
    
    return temp1, temp2, light1, light2, humidity1, humidity2, weekday, time, pir, led, light_accuracy, temp_accuracy

# def controlSwitch():
#     if ((sensor_data["fan"] == True) and (fan_state == False)):
#         time.sleep(2.5)
#         ser.write(b"true\n")
#         fan_state = True
#     if ((sensor_data["fan"] == False) and (fan_state == True)):
#         time.sleep(2.5)
#         ser.write(b"false\n")
#         fan_state = False
#     if ((sensor_data["led"] == True) and (led_state == False)):
#         time.sleep(2.5)
#         ser.write(b"on\n")
#         led_state = True
#     if ((sensor_data["led"] == False) and (led_state == True)):
#         time.sleep(2.5)
#         ser.write(b"off\n")
#         led_state = False

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
def setManualLight (params):
    sensor_data["Manual_light"] = params
    #print("Rx setValue is : ",sensor_data)
    print("Manual Light Set : ",params)
# Function will set the Fans
def setFan (params):
    sensor_data['fan'] = params
    #print("Rx setValue is : ",sensor_data)
    print("Fan Set : ",params)
def setManualFan (params):
    sensor_data['Manual_fan'] = params
    #print("Rx setValue is : ",sensor_data)
    print("Manual Fan Set : ",params)

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
            client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['Temperature1']), 1)
        if data['method'] == 'getLight':
            #print("getvalue request\n")
            #print("sent getValue : ", sensor_data)
            client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['LDR1']), 1)
            
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
        if data['method'] == 'setManualLight':
            #print("setvalue request\n")
            params = data['params']
            # print(f"Fan: Data is {data}\nParams are: {params}")
            setManualLight(params)
        if data['method'] == 'setFan':
            #print("setvalue request\n")
            params = data['params']
            # print(f"Fan: Data is {data}\nParams are: {params}")
            setFan(params)
        if data['method'] == 'setManualFan':
            #print("setvalue request\n")
            params = data['params']
            # print(f"Fan: Data is {data}\nParams are: {params}")
            setManualFan(params)

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
        # light1_data = round(random.uniform(0, 2400), 2)
        # light2_data = round(random.uniform(0, 2400), 2)
        # temp1_data = round(random.uniform(20, 35), 2)
        # temp2_data = round(random.uniform(20, 35), 2)
        # hum1_data = round(random.uniform(42, 72), 2)
        # hum2_data = round(random.uniform(42, 72), 2)
        # pir_data = round(random.uniform(0, 1))
        # weekday_data = round(random.uniform(0, 6))
        # time_data = round(random.uniform(0, 24))
        # Real Data
        weekday_data = datetime.datetime.now().isoweekday()
        time_data = datetime.datetime.now().hour
        
        if ((sensor_data["fan"] == True) and (fan_state == False)):
            time.sleep(2.5)
            ser.write(b"true\n")
            fan_state = True
        if ((sensor_data["fan"] == False) and (fan_state == True)):
            time.sleep(2.5)
            ser.write(b"false\n")
            fan_state = False
        if ((sensor_data["led"] == True) and (led_state == False)):
            time.sleep(2.5)
            ser.write(b"on\n")
            led_state = True
        if ((sensor_data["led"] == False) and (led_state == True)):
            time.sleep(2.5)
            ser.write(b"off\n")
            led_state = False
            
        if ser.in_waiting > 0:
            # sensor_data["temperature"] = ser.readline().decode("utf-8").rstrip()
            sensor_d = ser.readline().decode("utf-8").rstrip()
            sensor_arr = sensor_d.split(" ")
            print("Sensor Array: ", sensor_arr)
            for i in range(0, len(sensor_arr), 2):
                sensor_data[sensor_arr[i]] = sensor_arr[i+1]
                # print(f"I: {sensor_arr[i]}")
                # print(f"I+1: {sensor_arr[i+1]}")
                
            # print(f"Sensor Data: {sensor_data}")
        
        # new Dummy Sensor values
        # x = {
        #      "Temperature1": temp1_data,
        #      "Temperature2": temp2_data,
        #      "Humidity1": hum1_data,
        #      "Humidity2": hum2_data,
        #      "LDR1": float(sensor_data["LDR1"]),
        #      "LDR2": float(sensor_data["LDR2"]),
        #      "PIR_value": int(sensor_data["PIR_value"]),
        #      "weekday": weekday_data,
        #      "time": time_data
        #      }
        # new Sensor values
        x = {
             "Temperature1": float(sensor_data["Temperature1"]),
             "Temperature2": float(sensor_data["Temperature2"]),
             "Humidity1": float(sensor_data["Humidity1"]),
             "Humidity2": float(sensor_data["Humidity2"]),
             "LDR1": float(sensor_data["LDR1"]),
             "LDR2": float(sensor_data["LDR2"]),
             "PIR_value": int(sensor_data["PIR_value"]),
             "weekday": weekday_data,
             "time": time_data
             }
        
        x = {key: value for key, value in x.items() if value is not None}
        # ----------------- ML Model Fusion -----------------
        def write_read(x):
            ser.write(bytes(x, 'utf-8'))
            time.sleep(0.05)
            data = ser.readline()
            return data
        
        
        # ----------------- ML Model Fusion -----------------
        if (len(x) == 9):
            # model prediction
            temporary1 = x.copy()
            del temporary1["LDR1"]
            temporary2 = x.copy()
            del temporary2["Temperature1"]
            
            light_data = model_L.predict_one(temporary1)
            temp_data = model_T.predict_one(temporary2)
            model_L.learn_one(temporary1, x["LDR1"])
            model_T.learn_one(temporary2, x["Temperature1"])
            
            light_accuracy = metric1_L.update(x["LDR1"], light_data)
            temp_accuracy = metric1_T.update(x["Temperature1"], temp_data)
            
            if (sensor_data["Manual_light"] == False):
                if (light_data > 500):
                    sensor_data["led"] = True
                    # controlSwitch()
                else:
                    sensor_data["led"] = False
                    # controlSwitch()  
            else:
                # controlSwitch()
                pass
            
            if (sensor_data["Manual_fan"] == False):
                if (int(temp_data) <= 25):
                    sensor_data["fan"] = False
                    # controlSwitch()
                elif (int(temp_data) >= 30):
                    sensor_data["fan"] = True
                    # controlSwitch()
            else:
                # controlSwitch()
                pass
                # print(f"val = {val}")
        elif ((len(x) <= 5) and (("weekday" and "time" and "PIR_value" and "Humidity1") in x)):
            # model prediction
            if("LDR1" in x):
                temporary = x.copy()
                del temporary["LDR1"]
                light_data = model1_L_5.predict_one(temporary)
                model1_L_5.learn_one(temporary, x["LDR1"])
                light_accuracy = metric2_L.update(x["LDR1"], light_data)
                
                if (sensor_data["Manual_light"] == False):
                    if (light_data > 500):
                        sensor_data["led"] = True
                        # controlSwitch()
                    else:
                        sensor_data["led"] = False
                        # controlSwitch()  
                else:
                    # controlSwitch()
                    pass
            else:
                light_data = model1_L_5.predict_one(x)
                model1_L_5.learn_one(x, light_data)
                z = model1_L_5.predict_one(x)
                light_accuracy = metric2_L.update(light_data, z)
                
                if (sensor_data["Manual_light"] == False):
                    if (light_data > 500):
                        sensor_data["led"] = True
                        # controlSwitch()
                    else:
                        sensor_data["led"] = False
                        # controlSwitch()  
                else:
                    # controlSwitch()
                    pass
            
            if("Temperature1" in x):
                temporary = x.copy()
                del temporary["Temperature1"]
                temp_data = model1_T_5.predict_one(temporary)
                model1_T_5.learn_one(temporary, x["Temperature1"])
                temp_accuracy = metric2_T.update(x["Temperature1"], temp_data)
                
                if (sensor_data["Manual_fan"] == False):
                    if (int(temp_data) <= 25):
                        sensor_data["fan"] = False
                        # controlSwitch()
                    elif (int(temp_data) >= 30):
                        sensor_data["fan"] = True
                        # controlSwitch()
                else:
                    # controlSwitch()
                    pass
            else:
                temp_data = model1_T_5.predict_one(x)
                model1_T_5.learn_one(x, temp_data)
                z = model1_T_5.predict_one(x)
                light_accuracy = metric2_L.update(temp_data, z)
                
                if (sensor_data["Manual_fan"] == False):
                    if (int(temp_data) <= 25):
                        sensor_data["fan"] = False
                        # controlSwitch()
                    elif (int(temp_data) >= 30):
                        sensor_data["fan"] = True
                        # controlSwitch()
                    else:
                        # controlSwitch()
                        pass
                else:
                    val = write_read(str(sensor_data['fan']))
                    print(f"val = {val}")
        elif ((len(x) <= 5) and (("weekday" and "time" and "PIR_value" and "Humidity2") in x)):
            # model prediction
            if("LDR1" in x):
                temporary = x.copy()
                del temporary["LDR1"]
                light_data = model2_L_5.predict_one(temporary)
                model2_L_5.learn_one(temporary, x["LDR1"])
                light_accuracy = metric3_L.update(x["LDR1"], light_data)
                
                if (sensor_data["Manual_light"] == False):
                    if (light_data > 500):
                        sensor_data["led"] = True
                        # controlSwitch()
                    else:
                        sensor_data["led"] = False
                        # controlSwitch()  
                else:
                    # controlSwitch()
                    pass
            else:
                light_data = model2_L_5.predict_one(x)
                model2_L_5.learn_one(x, light_data)
                z = model2_L_5.predict_one(x)
                light_accuracy = metric3_L.update(light_data, z)
                
                if (sensor_data["Manual_light"] == False):
                    if (light_data > 500):
                        sensor_data["led"] = True
                        # controlSwitch()
                    else:
                        sensor_data["led"] = False
                        # controlSwitch()  
                else:
                    # controlSwitch()
                    pass
            
            if("Temperature1" in x):
                temporary = x.copy()
                del temporary["Temperature1"]
                temp_data = model2_T_5.predict_one(temporary)
                model2_T_5.learn_one(temporary, x["Temperature1"])
                temp_accuracy = metric3_T.update(x["Temperature1"], temp_data)
                
                if (sensor_data["Manual_fan"] == False):
                    if (int(temp_data) <= 25):
                        sensor_data["fan"] = False
                        # controlSwitch()
                    elif (int(temp_data) >= 30):
                        sensor_data["fan"] = True
                        # controlSwitch()
                    else:
                        # controlSwitch()
                        pass
            else:
                temp_data = model2_T_5.predict_one(x)
                model2_T_5.learn_one(x, temp_data)
                z = model2_T_5.predict_one(x)
                temp_accuracy = metric3_T.update(temp_data, z)
                
                if (sensor_data["Manual_fan"] == False):
                    if (int(temp_data) <= 25):
                        sensor_data["fan"] = False
                        # controlSwitch()
                    elif (int(temp_data) >= 30):
                        sensor_data["fan"] = True
                        # controlSwitch()
                    else:
                        # controlSwitch()
                        pass
        print("fan status: ", sensor_data["fan"])
        print("temp pred: ", temp_data)
        print("temp acc: ", temp_accuracy)
        print("Light pred: ", light_data)
        
        sensor_data = {
            **sensor_data,
            **x,
            "light accuracy": str(light_accuracy).split(" ")[1],
            "temp accuracy": str(temp_accuracy).split(" ")[1]
            }
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


