# SOLAR HYBRID INVERTER / CONTROLLER SYSTEM
A simple inverter app for gathering and monitoring your PV solar on-grid/off-grid system.  
Simply connect over USB-B type connector directly to the controller and you can start reading data.  
I've reversed engineered most of this from painfully reading registers and then checking on the actual PowMr device to see what it correlates to.

# Installation
1. Install python3 & pip:
    ```bash
    apt install python3-pip
    ```
3. Install minimalmodbus to communicate with controller:
   ```bash
   pip install minimalmodbus
   ```
5. Install Python FLASK module (for webpage):
   ```bash
   pip install flask
   ```
7. Connect over USB-B connecter (any common cable typical for connecting to a printer or USB hub) directly to the PowMr contoller (NOT RJ45 like a lot of bad documentation recommends)
8. Run the app!

# Example usage
```bash
./powmr.py check
```

# Questions?  Reach out to me seb@latestlinux.com
Enjoy!
