#include <Arduino.h>
#include <PulsePosition.h>
#include <sstream>
#include <string>

#define PPM_PIN 6
#define PWM1_PIN 2
#define PWM2_PIN 3
#define FAILSAFE_TIMEOUT 1000 // Failsafe timeout in milliseconds

// Define range values as global constants
const int THROTTLE_MIN = 1000;
const int THROTTLE_MAX = 2000;
const int STEERING_MIN = 1000;
const int STEERING_MAX = 2000;

// Define ONLY_AUTO_MODE and set it to TRUE to enable only automatic mode
#define ONLY_AUTO_MODE true

PulsePositionInput ppm(PPM_PIN);
unsigned long lastReceivedTime = 0;
bool failsafeActive = false;
bool automaticMode = false;

void setup()
{
  pinMode(PWM1_PIN, OUTPUT);
  pinMode(PWM2_PIN, OUTPUT);

  // Set the PWM resolution to 8 bits (0-255)
  analogWriteResolution(8);

  // Set the PWM frequency to the ideal frequency for 8-bit resolution
  analogWriteFrequency(PWM1_PIN, 500); // For 600 MHz or 450 MHz CPU speed
  analogWriteFrequency(PWM2_PIN, 500); // For 600 MHz or 450 MHz CPU speed

  Serial.begin(9600);
}

void executeCommand(const std::string &direction, int pwm1Percent, int pwm2Percent)
{
  int pwm1Speed, pwm2Speed;

  if (direction == "forward")
  {
    // Map PWM values to the forward range (188-65)
    pwm1Speed = map(pwm1Percent, 0, 100, 188, 65);
    pwm2Speed = map(pwm2Percent, 0, 100, 188, 65);
    analogWrite(PWM1_PIN, pwm1Speed);
    analogWrite(PWM2_PIN, pwm2Speed);
    Serial.println("Forward");
  }
  else if (direction == "right")
  {
    // Map PWM1 to the reverse range (196-255) and PWM2 to the forward range (188-65)
    pwm1Speed = map(pwm1Percent, 0, 100, 196, 255);
    pwm2Speed = map(pwm2Percent, 0, 100, 188, 65);
    analogWrite(PWM1_PIN, pwm1Speed);
    analogWrite(PWM2_PIN, pwm2Speed);
    Serial.println("Left");
  }
  else if (direction == "left")
  {
    // Map PWM1 to the forward range (188-65) and PWM2 to the reverse range (196-255)
    pwm1Speed = map(pwm1Percent, 0, 100, 188, 65);
    pwm2Speed = map(pwm2Percent, 0, 100, 196, 255);
    analogWrite(PWM1_PIN, pwm1Speed);
    analogWrite(PWM2_PIN, pwm2Speed);
    Serial.println("Right");
  }
  else if (direction == "brake")
  {
    analogWrite(PWM1_PIN, 250);
    analogWrite(PWM2_PIN, 250);
    delay(2000);
    analogWrite(PWM1_PIN, 0);
    analogWrite(PWM2_PIN, 0);
  }
  else if (direction == "stop")
  {
    // Stop both motors
    analogWrite(PWM1_PIN, 0);
    analogWrite(PWM2_PIN, 0);
  }
}

#if !ONLY_AUTO_MODE // If ONLY_AUTO_MODE is not set to TRUE, include manual control logic
void manualControl(int throttle, int steering)
{
  int pwm1 = map(throttle, THROTTLE_MIN + 100, THROTTLE_MAX, 0, 255); // Adjusted for manual control range
  int pwm2 = map(throttle, THROTTLE_MIN + 100, THROTTLE_MAX, 0, 255);

  // Adjust PWM based on steering
  if (steering < 1500)
  {
    pwm1 = map(steering, STEERING_MIN, 1500, 0, pwm1);
  }
  else if (steering > 1500)
  {
    pwm2 = map(steering, 1500, STEERING_MAX, pwm2, 0);
  }

  bool dir1 = (throttle > 1500);
  bool dir2 = (throttle > 1500);

  digitalWrite(DIR1_PIN, dir1);
  digitalWrite(DIR2_PIN, dir2);
  analogWrite(PWM1_PIN, pwm1);
  analogWrite(PWM2_PIN, pwm2);
}
#endif

void loop()
{
  if (ppm.available())
  {
    lastReceivedTime = millis();
    int throttle = ppm.read(1);
    int steering = ppm.read(2);
#if !ONLY_AUTO_MODE
    failsafeActive = (throttle < THROTTLE_MIN || throttle > THROTTLE_MAX || steering < STEERING_MIN || steering > STEERING_MAX);
    automaticMode = (throttle < THROTTLE_MIN + 100 && !failsafeActive); // Adjusted for automatic mode threshold
#else
    automaticMode = true; // Always in automatic mode when ONLY_AUTO_MODE is TRUE
#endif
  }

  if (automaticMode && Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim();
    std::istringstream iss(command.c_str());
    std::string direction;
    int pwm1Speed, pwm2Speed;
    char delimiter;
    getline(iss, direction, ',');
    iss >> pwm1Speed >> delimiter >> pwm2Speed;
    executeCommand(direction, pwm1Speed, pwm2Speed);
  }
#if !ONLY_AUTO_MODE
  else if (!automaticMode && !failsafeActive)
  {
    manualControl(ppm.read(1), ppm.read(2)); // Apply manual control logic
  }
#endif

  // Failsafe condition
  if (millis() - lastReceivedTime > FAILSAFE_TIMEOUT || failsafeActive)
  {
    failsafeActive = true;
    // Failsafe actions: stop motors
    analogWrite(PWM1_PIN, 0);
    analogWrite(PWM2_PIN, 0);
  }
}
