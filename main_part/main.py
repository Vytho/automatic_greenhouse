from display_init import SSD1306_I2C
import machine
import time
import ntptime
import network
from machine import Pin
import dht


# ---------------------------------------
# I2C DISPLAY CONFIGURATION
# ---------------------------------------
    # SDA --> GP0
    # SCL --> GP1
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# address scan - just for debugging now, later will be removed
print("I2C scan:", i2c.scan())

# scan the address
addrs = i2c.scan()

if not addrs:
    # will be used as log message ( could be handled by single function to make it
    # easier to include error time )
    print("Display can't be connected. Check address or wiring.")
    # someErrorHandler(code_of_error)
else:
    addr = addrs[0]
    # create SSD1306 instance (128x64) 
    oled = SSD1306_I2C(128, 64, i2c, addr=addr)


# Initial info on display
oled.fill(0)
oled.text("POWER:   ON", 0, 16)
oled.text("Wi-Fi:     ", 0, 32)
oled.show()




# ---------------------------------------
# TIME CONFIGURATION
# ---------------------------------------
    # If program fails to connect to network, or NTP can't
    # be accesed, program continues with warning and log messages
    # and other data do not have timestamp. ( controlled with DATE_IS_SET 
    # variable )

DATE_IS_SET = False

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("name", "password")

oled.fill_rect(0, 32, 128, 8, 0)  # clear Wi-Fi line
oled.text("Wi-Fi:", 0, 32)
oled.show()

# Simple animation while waiting for Wi-Fi
dots = ["", ".", "..", "..."]
dot_index = 0
timeout = 15

while not wlan.isconnected() and timeout > 0:
    oled.fill_rect(70, 32, 80, 8, 0)  # clear old dots
    oled.text(dots[dot_index], 68, 32)
    oled.show()
    dot_index = (dot_index + 1) % len(dots)
    time.sleep(0.5)
    timeout -= 1

# Final status
oled.fill_rect(70, 32, 80, 8, 0)  # clear animation
if wlan.isconnected():
    oled.text("ON", 72, 32)
    oled.show()
    try:
        ntptime.settime()
        DATE_IS_SET = True
    except:
        print("Could not get time from NTP")
else:
    oled.text("ERR", 72, 32)
    oled.show()
    print("Wi-Fi not connected, using default time")


# !!!!! custom localtime() funtion has to be written because of timezones !!!!
rtc = machine.RTC()



# ---------------------------------------
# BUTTONS CONFIGURATION
# ---------------------------------------
    # assuming pulled-up, so pressed = LOW
    # button 1 – manual watering --> GP0
    # button 2 – display + lights --> GP1
    # button 3 – change light mode --> GP2
BTN_WATER = Pin(2, Pin.IN, Pin.PULL_UP)
BTN_DISPLAY = Pin(3, Pin.IN, Pin.PULL_UP)
BTN_MODE = Pin(4, Pin.IN, Pin.PULL_UP) 

# ---------------------------------------
# SENSORS CONFIGURATION
# ---------------------------------------
# DHT11
dht11 = dht.DHT11(machine.Pin(5))


# ---------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------


def writeToData(tem, hum, timestamp, is_valid):
    with open("data_test.txt", "a") as file:
        if is_valid:
            file.write(f"{timestamp[0]}-{timestamp[1]}-{timestamp[2]} {timestamp[3]}:{timestamp[4]}:{timestamp[5]},{tem},{hum}\n")
        else:
            file.write(f"-,{tem},{hum}\n")



def readDataFromSensors(is_valid):
    # read from dht11 sensor
    dht11.measure()
    tem =dht11.temperature()
    hum = dht11.humidity()
    timestamp = time.localtime()
    writeToData(tem, hum, timestamp, is_valid)




# ---------------------------------------
# MAIN LOOP
# ---------------------------------------


# States
display_on = False
lights_on = False
party_mode = False
last_time = time.time()
DATA_INTERVAL = 600  # used to set interval for data measurement

while True:

    # Read data from sensors every 10 minutes
    curr_time = time.time()
    if curr_time - last_time >= DATA_INTERVAL:
        readDataFromSensors(DATE_IS_SET)
        last_time = curr_time





    # Button 1: manual watering
    if not BTN_WATER.value():   # pressed
        print("watering")
        time.sleep(0.3)  # debounce

    # Button 2: toggle display + lights
    if not BTN_DISPLAY.value():   # pressed
        display_on = not display_on
        lights_on = display_on
        if display_on:
            print("display is on")
            print("lights are turned on")
        else:
            print("display is off")
            print("lights are turned off")
            # clear the display
            oled.fill(0)
            oled.show()
        time.sleep(0.3)  # debounce

    # Button 3: change light mode
    if not BTN_MODE.value() and lights_on:   # pressed
        party_mode = not party_mode
        if party_mode:
            print("party mode")
        else:
            print("normal mode")
        time.sleep(0.3)  # debounce

    time.sleep(0.05)  # main loop delay






    # # vyčisti displej
    # oled.fill(0)

    # # jednoduchý nápis
    # oled.text("Ahoj, Pico W!", 0, 0)
    # oled.text("OLED 128x64 (I2C)", 0, 16)
    # oled.text("Toto je test.", 0, 32)

    # # môžeme nakresliť rámček
    # oled.rect(0, 0, 128, 64, 1)

    # oled.show()

    # # alternatívne bliknutie
    # time.sleep(2)
    # oled.fill(0)
    # oled.show()
    # time.sleep(0.5)
    # oled.text("Spusteny main.py", 0, 28)
    # oled.show()
# _______________________________________________________________


