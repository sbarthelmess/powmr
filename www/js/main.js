// Get Solar Data
async function getSolarData() {
    try {
        const response = await fetch('/solar');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const solar = await response.json();
	drawBattery(0, solar[0])
	drawBattery(1, solar[1])
	drawBattery(2, solar[2])
    } catch (error) {
        console.error('Failed to fetch solar data:', error);
    }
}
getSolarData()

function drawBattery(ui,data){
    const batteryLiquid = document.querySelectorAll('.battery__liquid')[ui],
          batteryStatus = document.querySelectorAll('.battery__status')[ui],
          batteryText = document.querySelectorAll('.battery__text')[ui],
          batteryPercentage = document.querySelectorAll('.battery__percentage')[ui]
    // Get battery ranges based on type
/*
    batt_min,batt_max = 0
    if (data.batt_type == "lifepo4") {
	batt_min = 42
	batt_max = 59.6
    } else if (data.batt_type == "gel") {
	batt_min = 40
	batt_max = 56
    } else {
	batt_min = 40
	batt_max = 58
    }
*/
    let level = Math.round(((data.battery_voltage-data.bat_min)/(data.bat_max-data.bat_min))*100); 
    batteryPercentage.innerHTML = `${level}%<font size=3> ${data.battery_voltage}V</font><br/><font size=4>${data.bat_type}</font>` 
    if (data.inv_amp>0.00) batteryLiquid.innerHTML += `<font size=2><p style="position:absolute;text-align:middle;bottom:50%;color:#300">Inv:${data.inv_amp}A</p>`
    if (data.grid_amp>0.00) batteryLiquid.innerHTML += `<font size=2><p style="position:absolute;text-align:middle;bottom:40%;color:#300">Grid:${data.grid_amp}A</p>`
    // Determine if charging or draining
    const charging = (data.solar_power - data.inv_power)
    // Determine if inverter is on, and then what the draw is (solar - inverter)
    const power = (Number(data.inv_power.parseInt)>60000)? 0 : (data.solar_power - data.inv_power);
    // Set battery visual size
    batteryLiquid.style.height = `${parseInt(level)}%`
    // Label battery and info
    batteryText.innerHTML = data.name;
    batteryStatus.innerHTML = `Solar: +${data.solar_power}W, Inv: -${data.inv_power}W<br/>`
    // Visualize current status
    if(level == 100){ /* We validate if the battery is full */
        batteryStatus.innerHTML += `Full battery <i class="ri-battery-2-fill green-color"></i>`
        batteryLiquid.style.height = '103%' /* To hide the ellipse */
    } else if(level <= 10 &! charging<1){ /* We validate if the battery is low */
        batteryStatus.innerHTML += `Low battery <i class="ri-plug-line animated-red"></i>`
    } else if(charging>0){ /* We validate if the battery is charging */
        batteryStatus.innerHTML += `Charging... ${charging}W<i class="ri-flashlight-line animated-green"></i>`
    } else if(power){ 
        batteryStatus.innerHTML += `Draining ${power}W <i class="ri-plug-line animated-red"></i>`
    } else {
	batteryStatus.innerHTML += `Inverter is off.`;
    }
    
    /* 4. We change the colors of the battery and remove the other colors */
    if(level <=20){
        batteryLiquid.classList.add('gradient-color-red')
        batteryLiquid.classList.remove('gradient-color-orange','gradient-color-yellow','gradient-color-green')
    }
    else if(level <= 40){
        batteryLiquid.classList.add('gradient-color-orange')
        batteryLiquid.classList.remove('gradient-color-red','gradient-color-yellow','gradient-color-green')
    }
    else if(level <= 80){
        batteryLiquid.classList.add('gradient-color-yellow')
        batteryLiquid.classList.remove('gradient-color-red','gradient-color-orange','gradient-color-green')
    }
    else{
        batteryLiquid.classList.add('gradient-color-green')
        batteryLiquid.classList.remove('gradient-color-red','gradient-color-orange','gradient-color-yellow')
    }
}
