# SOLAR HYBRID INVERTER / CONTROLLER SYSTEM
A complete inverter system app for gathering and monitoring your PV solar on-grid/off-grid system.  
Simply connect over USB-B type connector directly to the controller and you can start reading data.  
I've reversed engineered most of this from painfully reading registers and then checking on the actual PowMr device to see what it correlates to.

# NEW UPDATES
- Created powmr-multi.py, to handle multiple inverters.  Tricky since the USB order can change everytime you connect so I do some fancy device enumeration and tests to ensure they are the devices you expect.  Simple configuration inside the powmr-multi.py.
- Cool new website using uwsgi instead of weak Python-only flask webserver.
- Visualize your battery storage and solar/inverter/grid usage simply and beautifully using a custom CSS battery site I built.
- Many performance improvements (to powmr-multi.py). Keeping the old powrmr.py, but you'll want to migrate to the newer powmr-multi.py.

# Installation
1. Install python3 & pip:
    ```bash
    apt install python3-pip
    ```
2. Install minimalmodbus to communicate with controller:
   ```bash
   pip install minimalmodbus
   ```
3. Install NGINX, uwsgi, and Python FLASK module (for webpage):
   ```bash
   apt install nginx
   pip install uwsgi
   pip install flask
   ```
   Then install the uwsgi.service in /etc/systemd/system and enable.
4. Connect over USB-B connecter (any common cable typical for connecting to a printer or USB hub) directly to the PowMr contoller (NOT RJ45 like a lot of bad documentation recommends)
5. Run the app!

# Example usage
```bash
./powmr.py check
```

# Questions?  Reach out to me seb@latestlinux.com
Enjoy!
