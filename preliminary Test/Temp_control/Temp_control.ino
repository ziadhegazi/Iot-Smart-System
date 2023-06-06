#define ADC_VREF_V    5.0 // in volt
#define ADC_RESOLUTION 1024.0
#define PIN_LM35       A0
#define greenLed 8
#define yellowLed 9
#define redLed 10

String command;

void setup() {
    Serial.begin(9600);
    pinMode(greenLed, OUTPUT);
    pinMode(yellowLed, OUTPUT);
    pinMode(redLed, OUTPUT);
}

void loop() {
    // get the ADC value from the temperature sensor
    int adcVal = analogRead(PIN_LM35);
    // convert the ADC value to voltage in volt
    float milliVolt = adcVal * (ADC_VREF_V / ADC_RESOLUTION);
    // convert the voltage to the temperature in Celsius
    float tempC = milliVolt * 10;
    // convert the Celsius to Fahrenheit
    float tempF = tempC * 9 / 5 + 32;

    Serial.println(tempC);

    if (Serial.available()) {
        command = Serial.readStringUntil('\n');
        command.trim();

        if (command.equals("yellow")) {
            digitalWrite(yellowLed, HIGH);
            digitalWrite(greenLed, LOW);
            digitalWrite(redLed, LOW);
        }
        else if (command.equals("green")) {
            digitalWrite(yellowLed, LOW);
            digitalWrite(greenLed, HIGH);
            digitalWrite(redLed, LOW);
        }
        else if (command.equals("red")) {
            digitalWrite(yellowLed, LOW);
            digitalWrite(greenLed, LOW);
            digitalWrite(redLed, HIGH);
        }
        else if (command.equals("all")) {
            digitalWrite(yellowLed, HIGH);
            digitalWrite(greenLed, HIGH);
            digitalWrite(redLed, HIGH);
        }
        else if (command.equals("off")) {
            digitalWrite(yellowLed, LOW);
            digitalWrite(greenLed, LOW);
            digitalWrite(redLed, LOW);
        }
        else {
            digitalWrite(yellowLed, HIGH);
            digitalWrite(greenLed, HIGH);
            digitalWrite(redLed, HIGH);
        }
    }

    delay(1000);
}
