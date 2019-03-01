# External module imp
import RPi.GPIO as GPIO
import datetime
import time
import os
import Adafruit_ADS1x15 

wet_target = 15000
sensor_1 = 0 # these are the pin numbers on the ADS1115 board, labelled A0, A1, A2, A3
sensor_2 = 1
sensor_3 = 2
sensor_4 = 3
relay_1_pin = 31 # these are the GPIO pins attached to the relay board. Use which ones you want.
relay_2_pin = 33
relay_3_pin = 35
relay_4_pin = 37
initval = 20000 #arbitrary value to get pumping started. Moisture level will be checked every 'water_duration' seconds
water_duration = 5 # in seconds
delay = 1

init = False

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
GAIN = 1

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme

def get_last_watered():
    try:
        f = open("last_watered.txt", "r")
        return f.readline()
    except:
        return "NEVER!"

def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    GPIO.output(pin, GPIO.HIGH)
    
def auto_water():
    consecutive_water_count = 0
    for i in range(31, 39, 2):
 #      print(i)
       init_output(i)
    print("Auto-watering! Press CTRL+C to exit")
    try:
        while True:
          # Read the specified ADC channel using the previously set gain value.
            values = [0]*4
            for j in range(4):
                values[j] = adc.read_adc(j, gain=GAIN)
                if values[j] > dry:
                    if j == 0:
                        GPIO.output(relay_1_pin, GPIO.LOW)
                    elif j == 1:
                        GPIO.output(relay_2_pin, GPIO.LOW)
                    elif j == 2:
                        GPIO.output(relay_3_pin, GPIO.LOW)
                    elif j == 3:
                        GPIO.output(relay_4_pin, GPIO.LOW)
                elif j == 0:
                    GPIO.output(relay_1_pin, GPIO.HIGH)
                elif j == 1:
                    GPIO.output(relay_2_pin, GPIO.HIGH)
                elif j == 2:
                    GPIO.output(relay_3_pin, GPIO.HIGH)
                elif j == 3:
                    GPIO.output(relay_4_pin, GPIO.HIGH)
            time.sleep(water_duration)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        GPIO.cleanup() # cleanup all GPIO

def autowater_off():
    os.system("pkill -f water.py")
    for relay_pin in range(31, 39, 2):
        init_output(relay_pin)
        GPIO.output(relay_pin, GPIO.HIGH)

def pump_on(sensor_pin, relay_pin, wet_target):
#    print(str(sensor_pin) + " " + str(relay_pin) + " " + str(wet_target))
    init_output(relay_pin)
    f = open("last_watered.txt", "w")
    timeString = time.strftime('%d/%m/%Y %H:%M:%S')
    f.write("Last watered " + timeString)
    f.close()
	
    # Read the specified ADC channel using the previously set gain value.
    values = [0]*4
#    print(str(sensor_pin) + " " + str(relay_pin) + " " + str(wet_target))
    values[sensor_pin] = initval
    while values[sensor_pin] > wet_target:
        print(values[sensor_pin])
        GPIO.output(relay_pin, GPIO.LOW)
        time.sleep(water_duration)
        values[sensor_pin] = adc.read_adc(sensor_pin, gain=GAIN)		

    GPIO.output(relay_pin, GPIO.HIGH)
    return

def pump_all_on():
    f = open("last_watered.txt", "w")
    timeString = time.strftime('%d/%m/%Y %H:%M:%S')
    f.write("Last watered " + timeString)
    f.close()
    for i in range(31, 39, 2):
#       print(i)
       init_output(i)
    pump0 = 1
    pump1 = 1
    pump2 = 1
    pump3 = 1
    pumps_in_use = 4
    values = [0]*pumps_in_use
    GPIO.output(relay_1_pin, GPIO.LOW)
    GPIO.output(relay_2_pin, GPIO.LOW)
    GPIO.output(relay_3_pin, GPIO.LOW)
    GPIO.output(relay_4_pin, GPIO.LOW)
    while pumps_in_use > 0:
        for j in range(4):    
            print("Pumps in use = " + str(pumps_in_use))
            values[j] = adc.read_adc(j, gain=GAIN)  
            print("sensor " + str(j) + ", value = " + str(values[j]) + ", target = " + str(wet_target))
            if values[j] < wet_target:
                if j == 0:
                    GPIO.output(relay_1_pin, GPIO.HIGH)
                    print("stop pump " + str(j+1))	                    
                    if pump0 == 1: 
                        pumps_in_use = pumps_in_use - 1
                        pump0 = 0
                elif j == 1:
                    GPIO.output(relay_2_pin, GPIO.HIGH)
                    print("stop pump " + str(j+1))
                    if pump1 == 1: 
                        pumps_in_use = pumps_in_use - 1
                        pump1 = 0
                elif j == 2:
                    GPIO.output(relay_3_pin, GPIO.HIGH)
                    print("stop pump " + str(j+1))
                    if pump2 == 1: 
                        pumps_in_use = pumps_in_use - 1
                        pump2 = 0
                elif j == 3:
                    GPIO.output(relay_4_pin, GPIO.HIGH)
                    print("stop pump " + str(j+1))
                    if pump3 == 1: 
                        pumps_in_use = pumps_in_use - 1
                        pump3 = 0
        time.sleep(2)
    pumps_in_use = 0
    GPIO.output(relay_1_pin, GPIO.HIGH)
    GPIO.output(relay_2_pin, GPIO.HIGH)
    GPIO.output(relay_3_pin, GPIO.HIGH)
    GPIO.output(relay_4_pin, GPIO.HIGH)

def sensor_status(m1, m2, m3, m4):
    # Read all four ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = adc.read_adc(i, gain=GAIN)
        if values[i] > wet_target:
            if i == 0:
                m1 = "Water plant 1 please! "
            elif i==1:
                m2 = "Water plant 2 please! "
            elif i==2:
                m3 = "Water plant 3 please! "
            elif i==3:
                m4 = "Water plant 4 please! "
        else:
            if i == 0:
                m1 = "Plant 1 is happy! "
            elif i==1:
                m2 = "Plant 2 is happy! "
            elif i==2:
                m3 = "Plant 3 is happy! "
            elif i==3:
                m4 = "Plant 4 is happy! "
        text = water.get_last_watered()
    return text, m1, m2, m3, m4;
