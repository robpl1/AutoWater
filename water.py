# External module imp
from flask import Flask, render_template
import RPi.GPIO as GPIO
import datetime
import time
import os
import Adafruit_ADS1x15 

wet_target = 20000
sensor_1 = 0                   # these are the pin numbers on the ADS1115 board, labelled A0, A1, A2, A3
relay_1 = 8                    # these are the GPIO pins attached to the relay board. Use which ones you want.
water_duration = 1             # in seconds
waterfor = 5                  # in seconds
reading_interval = 1800        # in seconds
init = False

# Create an ADS1115 ADC (16-bit) instance and choose a Gain level
adc = Adafruit_ADS1x15.ADS1115()
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
GAIN = 1

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme

file = open("/home/pi/water_log.csv", "a") #' open the file in Append mode
if os.stat("/home/pi/water_log.csv").st_size == 0:
    file.write("Date and Time,Reading, Pump Status\n")
file.flush()
file.close()
file = open("/home/pi/infolog.csv", "a") #' open the file in Append mode
if os.stat("/home/pi/infolog.csv").st_size == 0:
    file.write("Date and Time,Information\n")
file.flush()
file.close()
file = open("/home/pi/pumplog.csv", "a") #' open the file in Append mode
if os.stat("/home/pi/pumplog.csv").st_size == 0:
    file.write("Date and Time,Information, Loop Count\n")
file.flush()
file.close()

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

def writedata(value,state):
    now = time.strftime('%d/%m/%Y %H:%M:%S')
    txt = now + ", sensor value: " + str(value) + ", pump state: " + state
    print(txt)
    file = open("/home/pi/water_log.csv", "a")
    file.write(now + "," + str(value) + "," + state +"\n")
    file.flush()
    file.close()

def writeinfo(info):
    now = time.strftime('%d/%m/%Y %H:%M:%S')
    txt = now + "," + info 
    print(txt)
    file = open("/home/pi/infolog.csv", "a")
    file.write(now + ", " + info + "\n")
    file.flush()
    file.close()

def writepumpinfo(info):
    now = time.strftime('%d/%m/%Y %H:%M:%S')
    txt = now + "," + info 
    print(txt)
    file = open("/home/pi/pumplog.csv", "a")
    file.write(now + ", " + info + "\n")
    file.flush()
    file.close()
    
def auto_water():
    init_output(relay_1)
    values = [0]
    count = 0
    read_interval = reading_interval
    print("Auto-watering! Use web page to stop")
    writeinfo("Auto-watering started")
    try:
        while True:
          # Read the specified ADC channel using the previously set gain value.
            values[sensor_1] = adc.read_adc(sensor_1, gain=GAIN)
            if values[sensor_1] > wet_target:
                print("Plant #" + str(sensor_1) + ", PumpPin #" + str(relay_1) + ", wet target = " + str(wet_target))
                writedata(values[sensor_1],"On")
                while values[sensor_1] > wet_target and count < waterfor: # Limit amount of watering to prevent overwatering. 
                                                                    # if the plant is still dry then watering 
                                                                    # will restart after a minute
                    GPIO.output(relay_1, GPIO.LOW)
                    values[sensor_1] = adc.read_adc(sensor_1, gain=GAIN)
                    count = count + 1
                    info = "Pumping -  Sensor value = " + str(values[sensor_1]) + ". Loop count = " + str(count)
                    writepumpinfo(info)
                    time.sleep(water_duration)
                GPIO.output(relay_1, GPIO.HIGH)
                writedata(values[sensor_1], "Off")
                count = 0
            else:
                count = 0
                now = time.strftime('%d/%m/%Y %H:%M:%S')
             #   print(now + " running pump - off, " + str(values[sensor_1]))
                writedata(values[sensor_1], "Off")
                #GPIO.output(relay_1, GPIO.HIGH)
            time.sleep(read_interval)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        os.system("pkill -f auto_water.py")
        file.flush()
        file.close()
        GPIO.cleanup() # cleanup all GPIO

def autowater_off():
    writeinfo("Auto-watering ended")
    init_output(relay_1)
    GPIO.output(relay_1, GPIO.HIGH)
    os.system("pkill -f auto_water.py")

def pump_on():
    print(str(sensor_1) + " " + str(relay_1) + " " + str(wet_target))
    init_output(relay_1)
    writeinfo("Pumping routine started")	
    # Read the specified ADC channel using the previously set gain value.
    values = [0]
    count = 0
    values[sensor_1] = adc.read_adc(0, gain=GAIN)
    print("Plant #" + str(sensor_1) + ", PumpPin #" + str(relay_1) + ", wet target = " + str(wet_target))
    print("Sensor reading = " + str(values[0]))
    if values[sensor_1] > wet_target:
        print("Sensor reading = " + str(values[0]))
        writedata(values[sensor_1],"On")
        while values[sensor_1] > wet_target and count < waterfor:
            GPIO.output(relay_1, GPIO.LOW)
            count = count + 1
            time.sleep(water_duration)
            values[sensor_1] = adc.read_adc(sensor_1, gain=GAIN)		
            info = "inside manual pump loop. Sensor value = " + str(values[sensor_1]) + ". Loop count = " + str(count)
            writepumpinfo(info)
        GPIO.output(relay_1, GPIO.HIGH)
        writedata(values[sensor_1],"Off")
        f = open("last_watered.txt", "w")
        timeString = time.strftime('%d/%m/%Y %H:%M:%S')
        f.write("Watered on " + timeString)
        f.close()
        watered = True
    else:
        watered = False
        print("pump not turned on because plant is wet")
    return watered

def sensor_status():
    # Read all ADC channel values in a list.
    values = [0]
    # Read the specified ADC channel using the previously set gain value.
    values[0] = adc.read_adc(0, gain=GAIN)
    print(values[0])
    t1 = get_last_watered()    
    if values[0] > wet_target:
        t2 = "Water plant please!" 
    else:
        t2 = "Plant is happy!"
    t3 = "Reading is " +  str(values[0])
    
    return t1, t2, t3;

