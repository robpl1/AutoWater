from flask import Flask, render_template, redirect, url_for
import psutil
import water
import os
import time
import RPi.GPIO as GPIO
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
water_duration = 10 # in seconds
m1 = ""
m2 = ""
m3 = ""
m4 = ""

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
GAIN = 1

app = Flask(__name__)

def template(title = "Auto-Water!", text = water.get_last_watered(), m1 = " ", m2 = " ", m3 = " ", m4 = " "):
    text, m1, m2, m3, m4 = status_report()
    templateData = {
        'title' : title,
        'text' : text,
        'm1' : m1,
        'm2' : m2,
        'm3' : m3,
        'm4' : m4
        }
    
    return templateData

def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    GPIO.output(pin, GPIO.HIGH)

def index():
    list_object = [m1, m2, m3, m4] 
    return render_template('main.html', text_to_send = list_object)

@app.route("/")
def main():
    text, m1, m2, m3, m4 = status_report()
    list_object = [text, m1, m2, m3, m4]
    return render_template('main.html', text_to_send = list_object)

@app.route("/last_watered")
def check_last_watered():
    text, m1, m2, m3, m4 = status_report()
    try:
        f = open("last_watered.txt", "r")
        text = f.readline()
#        text = "testing "
        list_object = [text, m1, m2, m3, m4]
    except:
        text =  "NEVER!"
        print(text)
        list_object = [text, m1, m2, m3, m4]
    return render_template('main.html', text_to_send = list_object)

@app.route("/sensor")
def sensor_status():
    text, m1, m2, m3, m4 = status_report()
#    text = "plant status"
    list_object = [m1, m2, m3, m4]
    return render_template('main.html', text_to_send = list_object)

def status_report():
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

@app.route("/water1")
def action1():
    water.pump_on(sensor_0, relay_1_pin, wet_target)
    text = "Watered plant 1 Once"
    list_object = [text]
    return render_template('main.html', text_to_send = list_object)

@app.route("/water2")
def action2():
    water.pump_on(sensor_1, relay_2_pin, wet_target)
    text = "Watered plant 2 Once"
    list_object = [text]
    return render_template('main.html', text_to_send = list_object)

@app.route("/water3")
def action3():
    water.pump_on(sensor_2, relay_3_pin, wet_target)
    text = "Watered plant 3 Once"
    return render_template('main.html', text_to_send = list_object)

@app.route("/water4")
def action4():
    water.pump_on(sensor_3, relay_4_pin, wet_target)
    text = "Watered plant 4 Once"
    list_object = [text]
    return render_template('main.html', text_to_send = list_object)

@app.route("/waterall")
def actionAll():
    water.pump_all_on()
    text = "Watered all plants once"
    list_object = [text]
    return render_template('main.html', text_to_send = list_object)

@app.route("/auto/water/<toggle>")
def auto_water(toggle):
    running = False
    if toggle == "ON":
        text = "Auto Watering On"
        list_object = [text]
        for process in psutil.process_iter():
            try:
                if process.cmdline()[1] == 'auto_water.py':
                    text = "Auto_Water is already running"
                    list_object = [text]
                    running = True
            except:
                pass
        if not running:
            os.system("python3 auto_water.py&")
            #water.auto_water()
    else:
        print("Autowater button off pressed")
        text = "Auto Watering Off"
        list_object = [text]
        water.autowater_off()

    return render_template('main.html', text_to_send = list_object)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
