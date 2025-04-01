#!/usr/bin/python3
"""
Driver for the PowMr Solar Controller using the Modbus RTU protocol
Connect directly from USB (host) -> USB-type B on the Inverter (NOT the RJ45 ports)
This will create a /dev/ttyUSB# device, just set that here
"""

import minimalmodbus
import time
import sys
from datetime import datetime
from flask import Flask

# Set Device constants (per your device)
UNITS="standard"
BAUD=9600
TIMEOUT=1.0
DEBUG=False
# Control register (for power on, off, & reset)
powMrControlReg=int("DF00",16)

# Read CLI command
CMD = ""
if len(sys.argv)>1:
  CMD = sys.argv[1]

# These are the registers read from WatchPower and determined by trial and error
powmr_registers = {
    "Battery Voltage": {'reg':257, 'multi':0.1, 'unit':'V', 'max':59.6},
    "Solar Voltage": {'reg':263, 'multi':0.1, 'unit':'V', 'max':400},
    "Solar Current": {'reg':548, 'multi':0.1, 'unit':'A', 'max':80},
    "Solar Power": {'reg':265, 'multi':1, 'unit':'W', 'max':1200},
    "Solar Temperature": {'reg':544, 'multi':0.1, 'unit':'C', 'max':110},
    "Inv Power": {'reg':539, 'multi':1, 'unit':'W','max':3500},
    "Battery Power In": {'reg':270, 'multi':0.1, 'unit':'W'},
    "Battery Current": {'reg':258, 'multi':0.1, 'unit':'A'},
}

"""
    "Ambient Temperature": {'reg':546, 'multi':0.1, 'unit':'C'},
    "Solar Temperature": {'reg':544, 'multi':0.1, 'unit':'C'},
    "Inv Temperature": {'reg':545, 'multi':0.1, 'unit':'C'},

    "Solar Voltage": {'reg':263, 'multi':0.1, 'unit':'V'},
    "Solar Current": {'reg':548, 'multi':0.1, 'unit':'A'},
    "Solar Power": {'reg':265, 'multi':1, 'unit':'W'},
    
    "Battery Voltage": {'reg':257, 'multi':0.1, 'unit':'V'},
    "Battery Power In": {'reg':270, 'multi':0.1, 'unit':'W'},
    "Battery Current": {'reg':258, 'multi':0.1, 'unit':'A'},
    
    "Inv Current": {'reg':537, 'multi':0.1, 'unit':'A'},
    "Inv Voltage": {'reg':534, 'multi':0.1, 'unit':'V'},
    "Inv VA": {'reg':540, 'multi':1, 'unit':'VA'},
    "Inv Power": {'reg':539, 'multi':1, 'unit':'W'},
    
    "Grid Voltage": {'reg':531, 'multi':0.1, 'unit':'V'},
    "Grid Current": {'reg':532, 'multi':0.1, 'unit':'A'},

    "Register 258" : {'reg':258, 'multi':1, 'unit':'na'}, # 	=>  15
    "Register 264" : {'reg':264, 'multi':1, 'unit':'na'}, # 	=>  1
    "Register 270" : {'reg':270, 'multi':1, 'unit':'na'}, # 	=>  0
    "Register 526" : {'reg':526, 'multi':1, 'unit':'na'}, # 	=>  3871
    "Register 530" : {'reg':530, 'multi':1, 'unit':'na'}, # 	=>  3145
    "Register 540" : {'reg':540, 'multi':1, 'unit':'na'}, # 	=>  72
    "Register 544" : {'reg':544, 'multi':1, 'unit':'na'}, # 	=>  132
    "Register 546" : {'reg':546, 'multi':1, 'unit':'na'}, # 	=>  215
    "Register 548" : {'reg':548, 'multi':1, 'unit':'na'}, #	=>  16

# Inverter settings (uninteresting)
    "Unknown Register 256" : {'reg':256, 'multi':1, 'unit':'na'}, # 	=>  28
    "Unknown Register 260" : {'reg':260, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 262" : {'reg':262, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 266" : {'reg':266, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 268" : {'reg':268, 'multi':1, 'unit':'na'}, # 	=>  0

# Inverter readings
    "Unknown Register 512" : {'reg':512, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 514" : {'reg':514, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 516" : {'reg':516, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 518" : {'reg':518, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 520" : {'reg':520, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 522" : {'reg':522, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 524" : {'reg':524, 'multi':1, 'unit':'na'}, # 	=>  4870
    "Unknown Register 528" : {'reg':528, 'multi':1, 'unit':'na'}, # 	=>  5
    "Unknown Register 532" : {'reg':532, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 534" : {'reg':534, 'multi':1, 'unit':'na'}, # 	=>  1200
    "Unknown Register 536" : {'reg':536, 'multi':1, 'unit':'na'}, # 	=>  5999
    "Unknown Register 538" : {'reg':538, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 542" : {'reg':542, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 550" : {'reg':550, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 552" : {'reg':552, 'multi':1, 'unit':'na'}, # 	=>  0A

# Inverter settings
    "Unknown Register 10" : {'reg':10, 'multi':1, 'unit':'na'}, # 	=>  65535
    "Unknown Register 12" : {'reg':12, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 14" : {'reg':14, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 16" : {'reg':16, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 18" : {'reg':18, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 20" : {'reg':20, 'multi':1, 'unit':'na'}, # 	=>  514
    "Unknown Register 22" : {'reg':22, 'multi':1, 'unit':'na'}, #	=>  300
    "Unknown Register 24" : {'reg':24, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 26" : {'reg':26, 'multi':1, 'unit':'na'}, # 	=>  1
    "Unknown Register 28" : {'reg':28, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 30" : {'reg':30, 'multi':1, 'unit':'na'}, # 	=>  65535
    "Unknown Register 32" : {'reg':32, 'multi':1, 'unit':'na'}, # 	=>  0
    "Unknown Register 34" : {'reg':34, 'multi':1, 'unit':'na'}, # 	=>  112
    "Unknown Register 36" : {'reg':36, 'multi':1, 'unit':'na'}, # 	=>  32
    "Unknown Register 38" : {'reg':38, 'multi':1, 'unit':'na'}, # 	=>  55
    "Unknown Register 40" : {'reg':40, 'multi':1, 'unit':'na'}, # 	=>  50
    "Unknown Register 42" : {'reg':42, 'multi':1, 'unit':'na'}, # 	=>  50
    "Unknown Register 44" : {'reg':44, 'multi':1, 'unit':'na'}, # 	=>  32
    "Unknown Register 46" : {'reg':46, 'multi':1, 'unit':'na'}, # 	=>  57
    "Unknown Register 48" : {'reg':48, 'multi':1, 'unit':'na'}, # 	=>  49
    "Unknown Register 50" : {'reg':50, 'multi':1, 'unit':'na'}, # 	=>  58
    "Unknown Register 52" : {'reg':52, 'multi':1, 'unit':'na'}, # 	=>  52
    "Unknown Register 54" : {'reg':54, 'multi':1, 'unit':'na'}, # 	=>  82
    "Unknown Register 56" : {'reg':56, 'multi':1, 'unit':'na'}, # 	=>  50
    "Unknown Register 58" : {'reg':58, 'multi':1, 'unit':'na'}, # 	=>  48
    "Unknown Register 60" : {'reg':60, 'multi':1, 'unit':'na'}, # 	=>  49
    "Unknown Register 62" : {'reg':62, 'multi':1, 'unit':'na'}, # 	=>  48
    "Unknown Register 64" : {'reg':64, 'multi':1, 'unit':'na'}, # 	=>  57
    "Unknown Register 66" : {'reg':66, 'multi':1, 'unit':'na'}, # 	=>  45
    "Unknown Register 68" : {'reg':68, 'multi':1, 'unit':'na'}, # 	=>  48
    "Unknown Register 70" : {'reg':70, 'multi':1, 'unit':'na'}, # 	=>  53
    "Unknown Register 72" : {'reg':72, 'multi':1, 'unit':'na'}, # 	=>  49
"""

import os.path
def find_usb():
    for x in range(10):
        if os.path.exists(f"/dev/ttyUSB{x}"): return(f"/dev/ttyUSB{x}")
    print("Can't find device... quitting")
    sys.exit(1)

def setup_dev():
    powMr=minimalmodbus.Instrument(find_usb(), 1)
    powMr.serial.baudrate = BAUD
    powMr.serial.timeout = TIMEOUT
    powMr.debug = DEBUG
    return powMr

def powMr_getData(DEBUG):
    powMr = setup_dev()
    for key, val in powmr_registers.items():
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            data = str(round(measurement,2)) + val['unit'];
            print(key," = ",data);
            time.sleep(.12)

        except Exception as e:
            print(e)
            sys.exit(1)

def powMr_csvSave():
    print(f"Entering CSV Save routine")
    powMr = setup_dev()
    csv_header="time,"
    csv_data=time.strftime("%m/%d/%y %H:%M")+","
    for key, val in powmr_registers.items():
        csv_header += key + ","
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            csv_data += str(round(measurement,2)) + val['unit'] + ","
            time.sleep(.12)

        except Exception as e:
            print(e)
            sys.exit(1)

    # Write to CSV file
    if not os.path.isfile("data.csv"):
        f=open("data.csv", "w")
        f.write(csv_header.rstrip(',')+"\n")
    else:
        f=open("data.csv", "a+")
    f.write(csv_data.rstrip(',')+"\n")
    f.close()

def powMr_save():
    import influxdb_client, os, time
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    token = "QfnMRMMZ4UunzVj6Kibvdty6ZL1Vxc48LkYo5b0t8IzlbUSQMMnJGQeV7ZOsJ8-xmSoPnmKeIkci5twSIj6yxA=="
    org = "solar"
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"
    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    powMr = setup_dev()
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    bucket="SolarData"
    for key, val in powmr_registers.items():
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            point = (
                Point("power")
                .tag("Inverter", "PowMr")
                .field(str(key+" in "+val['unit']), str(round(measurement,2)))
            )
            write_api.write(bucket=bucket, org=org, record=point)
            time.sleep(.3)
        except Exception as e:
            print(e)
            sys.exit(1)

def powMr_renderWWW():
    powMr = setup_dev()
    html = '<html><body style="background-color:black;color:white"'
    html += (f"{powMr.serial}<hr/>")
    for key, val in powmr_registers.items():
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            measurement = str(round(measurement,2))
            html += (f"{key}: {measurement} {val['unit']} ({val['max']})<br/>")
            time.sleep(.12)

        except Exception as e:
            print(e)
            sys.exit(1)
    return (html+'</body></html>')

def power_toggle(toggle):
    powMr = setup_dev()
    powMr.write_register(powMrControlReg,toggle,0)
    print(f"Inverter power reg {powMrControlReg} set to: {toggle}")

# Main App    
app = Flask(__name__)
@app.route('/')
def index():
    return powMr_renderWWW()

if __name__ == "__main__":
  if CMD == "save": 
    powMr_save()
  elif CMD == "csv": 
    powMr_csvSave()
  elif CMD == "debug":
    DEBUG=True
    powMr_getData(True)
  elif CMD == "check":
    DEBUG=False
    powMr_getData(True)
  elif CMD == "poweroff":
    power_toggle(0)
  elif CMD == "poweron":
    power_toggle(1)
  elif CMD == "web": # Serve webpage
    html='' # reset html
    app.run(debug=False, host='0.0.0.0')
  else:
    print(f"\nOption must be: save, check, debug, poweroff, poweron, or web.\n")
