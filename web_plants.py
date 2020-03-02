from flask import Flask, render_template, redirect, url_for
import psutil
import water
import os
import time

m1 = ""

app = Flask(__name__)

def template(title = "Auto-Water!", text = water.get_last_watered(), m1 = " ", m2 = " ", m3 = " ", m4 = " "):
    text, m1, m2, m3, m4 = status_report()
    templateData = {
        'title' : title,

        }
    return templateData

def index():
    list_object = [t1, t2, t3] 
    return render_template('main.html', text_to_send = list_object)

@app.route("/")
def main():
    t1, t2, t3 = water.sensor_status()
    list_object = [t1, t2, t3]
    return render_template('main.html', text_to_send = list_object)

@app.route("/water1")
def action1():
    watered = water.pump_on()
    t1, t2, t3 = water.sensor_status()
    if watered == False:
        t1 = "Pump not used. " + t1
    list_object = [t1, t2, t3]
    return render_template('main.html', text_to_send = list_object)

@app.route("/shutdown")
def shutdown():
    water.writeinfo("Closing auto-water program")
    os.system("pkill -f auto_water.py")
    os.system("pkill -f water.py")
    os.system("pkill -f web_plants.py")

@app.route("/auto/water/<toggle>")
def auto_water_web(toggle):
    running = False
    if toggle == "ON":
        print("Autowater button ON pressed")
        t1, t2, t3 = water.sensor_status()
        t1 = "Auto Watering On"
        list_object = [t1, t2, t3]
        for process in psutil.process_iter():
            try:
                if process.cmdline()[1] == 'auto_water.py':
                    t1 = "Auto_Water is already running"
                    list_object = [t1, t2, t3]
                    running = True
            except:
                pass
        if not running:
            os.system("python3 auto_water.py&")
            #water.auto_water()
    else:
        print("Autowater button OFF pressed")
        t1, t2, t3 = water.sensor_status()
        t1 = "Auto Watering Off"
        list_object = [t1, t2, t3]
        water.autowater_off()
    return render_template('main.html', text_to_send = list_object)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
