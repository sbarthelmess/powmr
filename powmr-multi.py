#!/usr/bin/python3
"""
SBarthelmess created complete solar inverter system for the PowMr Solar Controller using the Modbus RTU protocol
Connect directly from USB (host) -> USB-type B on the Inverter (NOT the RJ45 ports)
This will create a /dev/ttyUSB# device, just set that here
"""

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Begin CONFIGURATION SECTION, custom tailor these to your environment
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Set Device constants (per your device)
UNITS="standard"
BAUD=9600
TIMEOUT=3.0
DEBUG=False

# Define your inverters here, these are my examples 3 inverters, two in phase and the third as a backup
# INV1 - phase 1, INV2 - phase 2 (with grid backup), INV 3 - serves as "grid" to INV1 (also with grid backup)
inverters = [
    {'id':3,'dev':'0,3','name':'Basement','type':'GEL','max':50.8,'min':40},
    {'id':1,'dev':'1,1','name':'Tesla P1','type':'LifePO4','max':53.6,'min':42},
    {'id':2,'dev':'2,2','name':'Tesla P2','type':'LifePO4','max':53.6,'min':42}
]
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

from asynciominimalmodbus import Instrument
import time
import sys
from datetime import datetime
from flask import Flask
from flask import Response

# Control register (for power on, off, & reset)
powMrControlReg=int("DF00",16)

# Read CLI command
CMD = ""
if len(sys.argv)>1:
  CMD = sys.argv[1]

# These are the registers read from WatchPower and determined by trial and error
powmr_registers = {
    "battery_voltage": {'reg':257, 'multi':0.1, 'unit':'V', 'max':59.6},
    "solar_power": {'reg':265, 'multi':1, 'unit':'W', 'max':1200},
    "inv_power": {'reg':539, 'multi':1, 'unit':'W','max':3500},
    "inv_amp": {'reg':537, 'multi':0.1, 'unit':'A', 'max':40},
    "grid_amp": {'reg':532, 'multi':0.1, 'unit':'A', 'max':40},
}

"""
    "Battery Power In": {'reg':270, 'multi':0.1, 'unit':'W'},
    "Battery Current": {'reg':258, 'multi':0.1, 'unit':'A'},
    "Solar Voltage": {'reg':263, 'multi':0.1, 'unit':'V', 'max':400},
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
def find_usb(i):
    for x in range(i,128): # Try 128 USB files, return first one found
        if os.path.exists(f"/dev/ttyUSB{x}"): return(x)
    print("Can't find any devices... quitting")
    sys.exit(1)

def discover_dev(myDev):
    # First try "hinted" device
    try: 
        #print(f"Inverter hint:{inverters[myDev]['dev']}")
        hint_dev,hint_id = map(int, inverters[myDev]['dev'].split(','))
        powMr = setup_dev(hint_dev,hint_id)
        if (powMr): return powMr,myDev
    except IOError:
        print(f"Default device changed for {myDev}")
    # Try the first 128 IDs and return on first found...
    for myId in range(1,128): 
      try:
        powMr = setup_dev(myDev, myId)
        powMr.serial.timeout = 0.2 # Test quickly
        regs = powMr.read_register(257) # Validate battery voltage register
        print(f"\t-Found a PowMr solar device: {myDev}:{myId} (val: {regs})!")
        return powMr,myId
      except IOError:
        time.sleep(0.5)
    # None found in loop above, error out    
    print(f"- No valid PowMR devices found on /dev/ttyUSB{myDev}.")

def setup_dev(myDev, myId):
    powMr = Instrument(f"/dev/ttyUSB{myDev}", myId)
    powMr.serial.baudrate = BAUD
    powMr.serial.timeout = TIMEOUT
    powMr.debug = DEBUG
    return powMr
    
def powMr_getData(powMr):
    data = ""
    for key, val in powmr_registers.items():
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            val = str(round(measurement,2)) + val['unit']
            data = (f"{data}\n{key} = {val}");
            time.sleep(.12)
        except Exception as e:
            print(f"Error getting data: {e}")
    return data

def power_toggle(toggle):
    powMr = setup_dev(find_usb(0))
    print(f"- Inverter power reg {powMrControlReg} set to: {toggle}")
    powMr.write_register(powMrControlReg,toggle,1)
    print("DONE!")

def powMr_scan():
    powMr = setup_dev(find_usb(1))
    time.sleep(0.5)
    regs = powMr.read_registers(500,20)
    print("Read registers!")
    for idx in range(len(regs)):
        print(f"Register: {idx:3d} = {regs[idx]:5d} ({hex(regs[idx])})")
    time.sleep(0.5)

# Main App    
def getInverterData():
    try:
      print(f"Reading inverter: /dev/ttyUSB{i}")
      powMr,inv_id = discover_dev(find_usb(i))
      print(f"ID: {inv_id}, {inverters[i]['name']}")
      data = powMr_getData(powMr)
      print(f"DATA: {data}")
    except Exception as e:
      print(f"Error: {e}")

from multiprocessing import Process, Queue
def getInv1(q):
    powMr,inv_id = discover_dev(find_usb(0))
    q.put(powMr_getJSON(powMr,0))

def getInv2(q):
    powMr,inv_id = discover_dev(find_usb(1))
    q.put(powMr_getJSON(powMr,1))

def getInv3(q):
    powMr,inv_id = discover_dev(find_usb(2))
    q.put(powMr_getJSON(powMr,2))

def runMulti(*fns):
  q = Queue()
  proc = []
  data = []
  for fn in fns:
    p = Process(target=fn, args=(q,))
    proc.append(p)
    p.start()
  for p in proc:
    p.join()
    data.append(q.get()) # Will block
  return data

def powMr_getJSON(powMr,powMr_id):
    json = f"\"name\":\"{inverters[powMr_id]['name']}\",\"bat_type\":\"{inverters[powMr_id]['type']}\",\"bat_max\":\"{inverters[powMr_id]['max']}\",\"bat_min\":\"{inverters[powMr_id]['min']}\""
    for key, val in powmr_registers.items():
        try:
            measurement  = int(powMr.read_register(val['reg'])) * val['multi']
            if UNITS=='standard' and val['unit'] == 'C':
              measurement =(measurement * 9/5) + 32
              val['unit'] = 'F'
            measurement = str(round(measurement,2))
            json += f",\"{key}\":\"{measurement}\",\"{key}_unit\":\"{val['unit']}\""
            time.sleep(.12)
        except Exception as e:
            print(e)
            sys.exit(1)
    return "{"+json+"}"

if __name__ == "__main__":
  if CMD == "poweroff":
    power_toggle(0)
  elif CMD == "poweron":
    power_toggle(1)
  elif CMD == "web":
    app = Flask(__name__)
    @app.route('/solar')
    def home():
      inv_data = runMulti(getInv1,getInv2,getInv3)
      json_fmt = f"[ {inv_data[0]},\n{inv_data[1]},\n{inv_data[2]} ]"
      resp = Response(json_fmt)
      resp.headers['Access-Control-Allow-Origin'] = '*' 
      return resp
    app.run(debug=False, port=9875, host='0.0.0.0')
  elif CMD == "scan":
    powMr_scan()
  else:
    # Cycle through three inverters (guess their addresses, run in parallel)
    inv_data = runMulti(getInv1,getInv2,getInv3)
    json_fmt = f"[ {inv_data[0]},\n{inv_data[1]},\n{inv_data[2]} ]"
    print(f"JSON output: \n {json_fmt}")
    # Cycle through all known /dev/ttyUSBx devices
    #for i in range(0,len(inverters),1): 
    #  getInverterData();
