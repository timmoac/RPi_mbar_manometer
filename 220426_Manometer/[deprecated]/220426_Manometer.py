from serial import Serial
import time

# ----------------------
# Init
# ----------------------

serial_connect = Serial('COM14', 9600)
time.sleep(1)

while True:
    data = serial_connect.readline()
    pressure = str(data, 'UTF-8')

    print(pressure)

