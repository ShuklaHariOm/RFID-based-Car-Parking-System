#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <MFRC522.h>
#include <SPI.h>

// Pin configurations
#define RST_PIN 9  // Reset pin for RFID
#define SS_PIN 10  // Slave Select pin for RFID

// Define the Servo and LCD
Servo servoMotor;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // LCD I2C address 0x27
MFRC522 mfrc522(SS_PIN, RST_PIN);    // Create MFRC522 instance

// Define parking slots (5 slots for example)
#define TOTAL_SLOTS 4
int parkingSlots[TOTAL_SLOTS] = {0};  // 0 means available, 1 means occupied
String parkedCars[TOTAL_SLOTS];       // Stores RFID tag of the parked cars

void setup() {
  // Initialize components
  Serial.begin(9600);
  SPI.begin();            // Init SPI bus
  mfrc522.PCD_Init();     // Init RFID
  lcd.init();             // Init LCD
  lcd.backlight();        // Turn on LCD backlight
  servoMotor.attach(8);   // Servo connected to pin 8
  servoMotor.write(0);    // Initial position (barrier down)
  
  lcd.setCursor(0, 0);
  lcd.print("WELCOME!");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;  // No new card found
  }

  // Read the RFID UID (car's unique identifier)
  String carID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    carID += String(mfrc522.uid.uidByte[i], HEX);
  }

  // Serial.print("Car ID: ");
  // Serial.println(carID);

  // Check if the car is entering or exiting
  int slot = findCarSlot(carID);
  if (slot == -1) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WELCOME!");
    // New car, assign a parking slot if available
    int availableSlot = findAvailableSlot();
    if (availableSlot != -1) {
      // Assign slot and open the barrier
      assignSlot(availableSlot, carID);
    } else {
      // No slots available
      lcd.setCursor(0, 0);
      lcd.print("No slots avail");
      delay(2000);
      lcd.clear();
    }
  } else {
    // Car is exiting, free the slot
    freeSlot(slot);
  }

  // Halt PICC (prevents further communication until next read)
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

int findAvailableSlot() {
  for (int i = 0; i < TOTAL_SLOTS; i++) {
    if (parkingSlots[i] == 0) {
      return i;  // Slot is available
    }
  }
  return -1;  // No slots available
}

void assignSlot(int slot, String carID) {
  parkingSlots[slot] = 1;          // Mark slot as occupied
  parkedCars[slot] = carID;        // Store the car's RFID ID
  
  // Temporarily show parking information
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Park in Slot ");
  lcd.print(slot + 1);             // Display the slot number
  delay(2000);                     // Show this message for 2 seconds
  
  // Revert back to "WELCOME" message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WELCOME!");

  // Open the barrier
  servoMotor.write(90);            // Barrier up
  delay(3000);                     // Allow time for car to pass
  servoMotor.write(0);             // Barrier down

  // Send data to Python via serial
  Serial.print(carID);    // Car number (from RFID)
  Serial.print(",");      // Separator
  Serial.print(slot + 1); // Slot number
  Serial.println(",entry");   // Entry status

}

void freeSlot(int slot) {
  parkingSlots[slot] = 0;          // Mark slot as free
  
  // Temporarily show exit information
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Slot ");
  lcd.print(slot + 1);
  lcd.print(" is free");
  delay(2000);                     // Show this message for 2 seconds
  
  // Revert back to "WELCOME" message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TY Visit Again!");
  delay(3000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WELCOME!");

  // Open the barrier
  servoMotor.write(90);            // Barrier up
  delay(3000);                     // Allow time for car to pass
  servoMotor.write(0);             // Barrier down

  // Send data to Python via serial
  Serial.print(parkedCars[slot]);    // Car number
  Serial.print(",");                // Separator
  Serial.print(slot + 1);           // Slot number
  Serial.println(",exit");          // Exit status
}

int findCarSlot(String carID) {
  for (int i = 0; i < TOTAL_SLOTS; i++) {
    if (parkingSlots[i] == 1 && parkedCars[i] == carID) {
      return i;  // Found the car in a slot
    }
  }
  return -1;  // Car is not in the parking lot
}