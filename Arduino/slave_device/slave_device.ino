// put your setup code here, to run once:
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_INA219.h>

// Setting up Current Sensor 
Adafruit_INA219 ina219_1 (0x40);
//  Setting up Fans (motor driver)
const int IN4 = 8;
const int IN3 = 9;
const int IN2 = 10;
const int IN1 = 11;
int ENA = 7;
int ENB = 12;

// Set DHT type
#define DHTTYPE DHT22   // DHT 22  (AM2302)

// Set DHT pins:
#define DHT1_pin 2
#define DHT2_pin 3

// Initialize DHT sensor for normal 16mhz Arduino:
DHT dht1 = DHT(DHT1_pin, DHTTYPE);
DHT dht2 = DHT(DHT2_pin, DHTTYPE);

// Set LDR pins
#define LDR1_pin A0
#define LDR2_pin A1
// LDR Characteristics
const float GAMMA = 0.7;
const float RL10 = 50;

// PIR setup
// ----------------- change LED later
int PIR_ledPin = 13;                // choose the pin for the LED
int PIR_inputPin = 5;               // choose the input pin (for PIR sensor)
int pirState = LOW;             // we start, assuming no motion detected
int PIR_val;                    // variable for reading the pin status

// LED
#define LED_PIN 6 // must support PWM

String command;

void setup() {
  Serial.begin(9600);
  
  while (!Serial) {
      // will pause Zero, Leonardo, etc until serial console opens
      delay(1);
  }

      
  // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
  if (! ina219_1.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) { delay(10); }
  }
  // To use a slightly lower 32V, 1A range (higher precision on amps):
  //ina219.setCalibration_32V_1A();
  // Or to use a lower 16V, 400mA range (higher precision on volts and amps):
  ina219_1.setCalibration_16V_400mA();

  // Setup sensor:
  // DHT
  dht1.begin();
  dht2.begin();
  // PIR
  pinMode(PIR_ledPin, OUTPUT);      // declare LED as output
  pinMode(PIR_inputPin, INPUT);     // declare sensor as input
  // LED
  pinMode(LED_PIN, OUTPUT);
  // Fans
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
}

void loop() {
  // wait a few seconds between measurements.
  delay(2000);

  // Read Current sensor
  // For fans
  float shuntvoltage1 = 0;
  float busvoltage1 = 0;
  float current_mA1 = 0;
  float loadvoltage1 = 0;
  float power_mW1 = 0;
  shuntvoltage1 = ina219_1.getShuntVoltage_mV();
  busvoltage1 = ina219_1.getBusVoltage_V();
  current_mA1 = ina219_1.getCurrent_mA();
  power_mW1 = ina219_1.getPower_mW();
  loadvoltage1 = busvoltage1 + (shuntvoltage1 / 1000);

  // read humidity
  float humi1  = dht1.readHumidity();
  float humi2  = dht2.readHumidity();
  // read temperature as Celsius
  float tempC1 = dht1.readTemperature();
  float tempC2 = dht2.readTemperature();
  // Read LDR
  int LDR1 = analogRead(LDR1_pin);
  float voltage1 = LDR1 / 1024. * 5;
  float resistance1 = 2000 * voltage1 / (1 - voltage1 / 5);
  float lux1 = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance1, (1 / GAMMA));

  int LDR2 = analogRead(LDR2_pin);
  float voltage2 = LDR2 / 1024. * 5;
  float resistance2 = 2000 * voltage2 / (1 - voltage2 / 5);
  float lux2 = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance2, (1 / GAMMA));
  // Read PIR
  PIR_val = digitalRead(PIR_inputPin);  // read input value
  // Serial.println(PIR_val);

  // ----------------- Output -----------------
  // check if any reads failed From DHT 1
  if (isnan(humi1)) {
    // Serial.print("  |  ");
    Serial.print("Humidity1 ");
    Serial.print("Failed_to_read_Humidity_from_DHT1_sensor!");
  }if (isnan(tempC1)) {
    // Serial.print("  |  ");
    Serial.print(" "); 
    Serial.print("Temperature1 ");
    Serial.print("Failed_to_read_Temperature_from_DHT1_sensor!");
  } else {
    // Serial.print("  |  ");

    Serial.print("Humidity1 ");
    Serial.print(humi1);
    // Serial.print("%");

    // Serial.print("  |  "); 
    Serial.print(" "); 

    Serial.print("Temperature1 ");
    Serial.print(tempC1);
    // Serial.print("°C ~ ");
  }

  // check if any reads failed from DHT2
  if (isnan(humi2)) {
    // Serial.print("  |  ");
    Serial.print(" "); 
    Serial.print("Humidity2 ");
    Serial.print("Failed_to_read_Humidity_from_DHT2_sensor!");
  }if (isnan(tempC2)) {
    // Serial.print("  |  ");
    Serial.print(" "); 
    Serial.print("Temperature2 ");
    Serial.print("Failed_to_read_Temperature_from_DHT2_sensor!");
  } else {
    // Serial.print("  |  ");
    Serial.print(" "); 

    Serial.print("Humidity2 ");
    Serial.print(humi2);
    // Serial.print("%");

    // Serial.print("  |  "); 
    Serial.print(" "); 

    Serial.print("Temperature2 ");
    Serial.print(tempC2);
    // Serial.print("°C ~ ");
  }

  // check if any reads failed from LDR1
  if (isnan(LDR1)) {
    // Serial.print("  |  "); 
    Serial.print(" "); 
    Serial.print("LDR1 ");
    Serial.print("Failed_to_read_from_LDR1_sensor!");
  } else {
    // Serial.print("  |  "); 
    Serial.print(" "); 

    Serial.print("LDR1 ");
    Serial.print(lux1);
  }

  // check if any reads failed from LDR2
  if (isnan(LDR2)) {
    // Serial.print("  |  "); 
    Serial.print(" "); 
    Serial.print("LDR2 ");
    Serial.print("Failed_to_read_from_LDR2_sensor!");
  } else {
    // Serial.print("  |  ");
    Serial.print(" ");  

    Serial.print("LDR2 ");
    Serial.print(lux2);
  }

  // Serial.print("  |  ");
  Serial.print(" "); 
   
  Serial.print("PIR_value ");
  Serial.print(PIR_val);
  if (PIR_val == 1) {            // check if the input is HIGH
    digitalWrite(PIR_ledPin, HIGH);  // turn LED ON
    if (pirState == LOW) {
      // we have just turned on
      // Serial.print("  |  "); 
      // Serial.println("Motion detected!");
      // We only want to print on the output change, not state
      pirState = HIGH;
    }
  } else {
    digitalWrite(PIR_ledPin, LOW); // turn LED OFF
    if (pirState == HIGH){
      // we have just turned of
      // Serial.print("  |  "); 
      // Serial.println("Motion ended!");
      // We only want to print on the output change, not state
      pirState = LOW;
    }
  }

  Serial.print(" ");
  Serial.print("Bus_Voltage_For_Fans_(V) "); 
  Serial.print(busvoltage1);

  Serial.print(" ");
  Serial.print("Shunt_Voltage_For_Fans_(mV) "); 
  Serial.print(shuntvoltage1);

  Serial.print(" ");
  Serial.print("Load_Voltage_For_Fans_(V) "); 
  Serial.print(loadvoltage1);

  Serial.print(" ");
  Serial.print("Current_For_Fans_(mA) "); 
  Serial.print(current_mA1);

  Serial.print(" ");
  Serial.print("Power_For_Fans_(mW) "); 
  Serial.println(power_mW1);

  // ----------------- Control -----------------
  // LED control
  float norm_lux = (lux2 - 0.1)/ (3000 - 0.1);
  // Serial.print("Norm: ");
  // Serial.print(norm_lux);

  // Serial.print("  |  ");

  // Serial.print("bit: ");
  // Serial.println(norm_lux*255);

  analogWrite(LED_PIN, 255/(norm_lux*255));

  // int sensor_reading[7] = {humi1, tempC1, humi2, tempC2, lux1, lux2, PIR_val};

  analogWrite(ENA, 255); // Send PWM signal to L298N Enable pin
  analogWrite(ENB, 255); // Send PWM signal to L298N Enable pin
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    Serial.println(command);
}

  delay(1000);
}
