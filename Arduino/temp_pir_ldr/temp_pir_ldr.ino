// put your setup code here, to run once:
#include <Adafruit_Sensor.h>
#include <DHT.h>

// Set DHT type, uncomment whatever type you're using!
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
int PIR_inputPin = 4;               // choose the input pin (for PIR sensor)
int pirState = LOW;             // we start, assuming no motion detected
int PIR_val = 0;                    // variable for reading the pin status

// LED
#define LED_PIN 6 // must support PWM

void setup() {
  Serial.begin(9600);

  // Setup sensor:
  // DHT
  dht1.begin();
  dht2.begin();
  // PIR
  pinMode(PIR_ledPin, OUTPUT);      // declare LED as output
  pinMode(PIR_inputPin, INPUT);     // declare sensor as input
  // LED
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  // wait a few seconds between measurements.
  delay(2000);

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
  if (isnan(humi1) || isnan(tempC1)) {
    Serial.println("Failed to read from DHT1 sensor!");
  } else {
    Serial.print("  |  ");

    Serial.print("Humidity1: ");
    Serial.print(humi1);
    Serial.print("%");

    Serial.print("  |  "); 

    Serial.print("Temperature1: ");
    Serial.print(tempC1);
    Serial.print("°C ~ ");
  }

  // check if any reads failed from DHT2
  if (isnan(humi2) || isnan(tempC2)) {
    Serial.println("Failed to read from DHT2 sensor!");
  } else {
    Serial.print("  |  ");

    Serial.print("Humidity2: ");
    Serial.print(humi2);
    Serial.print("%");

    Serial.print("  |  "); 

    Serial.print("Temperature2: ");
    Serial.print(tempC2);
    Serial.print("°C ~ ");
  }

  // check if any reads failed from LDR1
  if (isnan(LDR1)) {
    Serial.println("Failed to read from LDR1 sensor!");
  } else {
    Serial.print("  |  "); 

    Serial.print("LDR1: ");
    Serial.print(lux1);
  }

  // check if any reads failed from LDR2
  if (isnan(LDR2)) {
    Serial.println("Failed to read from LDR2 sensor!");
  } else {
    Serial.print("  |  "); 

    Serial.print("LDR2: ");
    Serial.println(lux2);
  }

  if (PIR_val == HIGH) {            // check if the input is HIGH
    digitalWrite(PIR_ledPin, HIGH);  // turn LED ON
    if (pirState == LOW) {
      // we have just turned on
      Serial.print("  |  "); 
      Serial.println("Motion detected!");
      // We only want to print on the output change, not state
      pirState = HIGH;
    }
  } else {
    digitalWrite(PIR_ledPin, LOW); // turn LED OFF
    if (pirState == HIGH){
      // we have just turned of
      Serial.print("  |  "); 
      Serial.println("Motion ended!");
      // We only want to print on the output change, not state
      pirState = LOW;
    }
  }

  // LED control
  float norm_lux = (lux2 - 0.1)/ (3000 - 0.1);
  Serial.print("Norm: ");
  Serial.print(norm_lux);

  Serial.print("  |  ");

  Serial.print("bit: ");
  Serial.println(norm_lux*255);

  analogWrite(LED_PIN, 255/(norm_lux*255));

}
