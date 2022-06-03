from machine import Pin, I2C, UART
import time
import os

# ----------------------
# Init
# ----------------------

# Initialisierung I2C-Pins
i2c_sda = Pin(16)
i2c_scl = Pin(17)

# Initialisierung I2C
i2c = I2C(0,sda=i2c_sda,scl=i2c_scl,freq=200000)

# Init UART
uart = UART(0, baudrate = 9600)
time.sleep(3)

# ----------------------
# Func Def
# ----------------------
    
def bytes2binstr(b, n=None):
    """
    converts bytes to binary string
    """
    s = ''.join(f'{x:08b}' for x in b)
    return s if n is None else s[:n + n // 8 + (0 if n % 8 else -1)]


def get_temp(adress):
    """
    gets temperature readout from i2c device connected at adress
    """
    four_byte_hex = i2c.readfrom(adress, 4)
    four_byte_bin = bytes2binstr(four_byte_hex, n=32)
    temp_readout = four_byte_bin[16:27]
    temperature = (int(temp_readout, 2)*200/2047)-50
    return temperature


def get_pressure(adress):
    """
    gets pressure readings in mbar from i2c device connected at adress
    """
    output_max = 14746
    output_min = 1638 
    pressure_max = 5*68.9475729317831  
    pressure_min = -5*68.9475729317831
    
    four_byte_hex = i2c.readfrom(adress, 4)
    four_byte_bin = bytes2binstr(four_byte_hex, n=32)
    pressure_readout = four_byte_bin[2:16]
    pressure = (((int(pressure_readout, 2) - output_min) * (pressure_max - pressure_min) / (output_max - output_min)) + pressure_min)
    
    return pressure


# ----------------------
# Run
# ----------------------


while True:
    pressure = get_pressure(0x28)
    print(pressure)

    def current_milli_time():
    return round(time.time() * 1000)

    uart.write(str(pressure), current_milli_time())
        
    time.sleep_ms(50)
        
