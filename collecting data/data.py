import serial
import datetime
import time

if __name__ == "__main__":
    # ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
    ser = serial.Serial("COM9", 9600, timeout = 1)
    # ser = serial.Serial("/dev/ttyACM0", 9600, timeout = 1)
    ser.flush()
    
sensor_data = {}

while True:
    weekday_data = datetime.datetime.now().isoweekday()
    time_data = datetime.datetime.now().hour
    if ser.in_waiting > 0:
        # # sensor_data["temperature"] = ser.readline().decode("utf-8").rstrip()
        sensor_d = ser.readline().decode("utf-8").rstrip()
        sensor_arr = sensor_d.split(" ")
        # print("Sensor Array: ", sensor_arr)
        for i in range(0, len(sensor_arr), 2):
            # sensor_data[sensor_arr[i]] = sensor_arr[i+1]
            # print(f"I: {sensor_arr[i]}")
            # print(f"I+1: {sensor_arr[i+1]}")
            if ((sensor_arr[i] == "Temperature1") or (sensor_arr[i] == "Temperature2") or (sensor_arr[i] == "LDR1") or (sensor_arr[i] == "LDR2") or (sensor_arr[i] == "Humidity1") or (sensor_arr[i] == "Humidity2") or (sensor_arr[i] == "PIR_value") or (sensor_arr[i] == "weekday") or (sensor_arr[i] == "time")):
                # sensor_data[sensor_arr[i]] = sensor_arr[i+1].split(" ")[1]
                sensor_data[sensor_arr[i]] = sensor_arr[i+1]
        sensor_data = {key: value for key, value in sensor_data.items() if value is not None}
        data = []
        for val in sensor_data.values():
            # print(val)
            data.append(val)
        print(data)
        # for val in sensor_data:
        #     print(val)

        #         # data.append(val)
        # f = open("demofile2.csv", "a")
        # f.write(str(data)+"\n")
        # # f.write(f"{array}\n")
        # f.close()
        ser.write(b"true\n")
        time.sleep(4.5)
        ser.write(b"false\n")
        time.sleep(4.5)