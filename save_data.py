import serial
import sqlite3
from datetime import datetime

# Connect to the SQLite database
try:
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    print("Connected to the database successfully.")
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")

# Connect to the serial port
try:
    ser = serial.Serial('COM5', 9600)
    print("Serial port connected successfully.")
except serial.SerialException as e:
    print(f"Error connecting to serial port: {e}")

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"Received data: {data}")
        
        # Parse the data received from Arduino
        try:
            car_number, slot_number, status = data.split(',')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing data: {e}")
            continue
        
        try:
            if status == "entry":
                # Insert entry data into the database
                cursor.execute("INSERT INTO parking_data (car_number, in_time, slot_number) VALUES (?, ?, ?)",
                               (car_number, now, slot_number))
                conn.commit()
                print(f"Car {car_number} entry at {now} in slot {slot_number}")
            
            elif status == "exit":
                # Update the database with the exit time
                cursor.execute("UPDATE parking_data SET out_time = ? WHERE car_number = ? AND slot_number = ?",
                               (now, car_number, slot_number))
                conn.commit()
                print(f"Car {car_number} exit at {now} in slot {slot_number}")
        except sqlite3.Error as e:
            print(f"Database operation error: {e}")
