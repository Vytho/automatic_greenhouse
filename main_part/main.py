from display_init import SSD1306_I2C
import machine
import time
import ntptime
import network
from machine import Pin
import dht


#####################################
# ----------CONFIGURATION -----------
#####################################

# ---------------------------------------
# I2C DISPLAY
# ---------------------------------------
    # SDA --> GP0
    # SCL --> GP1
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# scan the address
addrs = i2c.scan()

if not addrs:
    # will be used as log message ( could be handled by single function to make it
    # easier to include error time )
    print("Display can't be connected. Check address or wiring.")
else:
    # Use first address and create SSD1306 instance (128x64) 
    addr = addrs[0]
    oled = SSD1306_I2C(128, 64, i2c, addr=addr)


# Initial info on display when turned on
oled.fill(0)
oled.text("POWER:   ON", 0, 16)
oled.text("Wi-Fi:     ", 0, 32)
oled.show()




# ---------------------------------------
# TIME AND WI-FI
# ---------------------------------------
    # If program fails to connect to network, or NTP can't
    # be accesed, program continues with warning and log messages
    # and other data do not have timestamp. ( controlled with DATE_IS_SET 
    # variable )
DATE_IS_SET = False             # Check, if timestamps can be created
DOTS = ["", ".", "..", "..."]
TIMEOUT = 20                    # How long to wait before proceeding without Wi-Fi connection
dot_index = 0


# Make login to wi-fi secure, so that you can push to github ;)
with open("password.txt", "r") as file:
    NAME = file.readline().strip()
    PASSWORD = file.readline().strip()


# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(NAME, PASSWORD)

oled.fill_rect(0, 32, 128, 8, 0)  # clear Wi-Fi line
oled.text("Wi-Fi:", 0, 32)
oled.show()



while not wlan.isconnected() and TIMEOUT > 0:
    oled.fill_rect(70, 32, 80, 8, 0)  # clear old dots
    oled.text(DOTS[dot_index], 68, 32)
    oled.show()
    dot_index = (dot_index + 1) % len(DOTS)
    time.sleep(0.5)
    TIMEOUT -= 1

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


rtc = machine.RTC()


# ---------------------------------------
# BUTTONS
# ---------------------------------------
    # assuming pulled-up, so pressed = LOW
    # button 1 – manual watering --> GP6
    # button 2 – display + lights --> GP7
    # button 3 – change light mode --> GP8
BTN_WATER = Pin(6, Pin.IN, Pin.PULL_UP)
BTN_DISPLAY = Pin(7, Pin.IN, Pin.PULL_UP)
BTN_MODE = Pin(8, Pin.IN, Pin.PULL_UP) 


# ---------------------------------------
# DHT11 / MOTOR DRIVER / RGB LED
# ---------------------------------------
dht11 = dht.DHT11(machine.Pin(9))

motor_a = Pin(15, Pin.OUT)  # B-1A
motor_b = Pin(14, Pin.OUT)  # B-1B

led_r = Pin(18, Pin.OUT)
led_g = Pin(19, Pin.OUT)
led_b = Pin(20, Pin.OUT)




#####################################
# --------HELPER FUNCTIONS ----------
#####################################

def last_sunday(year, month):
    """Return day of month for last Sunday in given month/year"""
    # Go to the first day of next month
    if month == 12:
        next_month = (year + 1, 1, 1, 0, 0, 0, 0, 0)
    else:
        next_month = (year, month + 1, 1, 0, 0, 0, 0, 0)
    ts = time.mktime(next_month)
    ts -= 24 * 3600  # step back one day
    while time.localtime(ts)[6] != 6:  # 6 = Sunday
        ts -= 24 * 3600
    return time.localtime(ts)[2]

def is_dst_eu(year, month, day, hour):
    """Check if given UTC time is in EU DST period (Slovakia included)"""
    dst_start = last_sunday(year, 3)   # March
    dst_end   = last_sunday(year, 10)  # October

    if 3 < month < 10:
        return True
    if month < 3 or month > 10:
        return False
    if month == 3:
        if day > dst_start or (day == dst_start and hour >= 2):
            return True
    if month == 10:
        if day < dst_end or (day == dst_end and hour < 3):
            return True
    return False

def changeByTimezone(utc_tuple):
    """Convert UTC tuple to Slovakia localtime (CET/CEST)"""
    year, month, day, hour, minute, second, wday, yday = utc_tuple
    offset = 3600  # CET = UTC+1
    if is_dst_eu(year, month, day, hour):
        offset = 7200  # CEST = UTC+2
    return time.localtime(time.mktime(utc_tuple) + offset)





def writeToData(tem, hum, timestamp, is_valid):
    with open("data_test.txt", "a") as file:
        if is_valid:
            file.write(f"{timestamp[0]}-{timestamp[1]}-{timestamp[2]} {timestamp[3]}:{timestamp[4]}:{timestamp[5]},{tem},{hum}\n")
            print("data written")
        else:
            file.write(f"-,{tem},{hum}\n")
            print("data written, date not found")

def readDataFromSensors(is_valid):
    try:
        # read from dht11 sensor
        dht11.measure()
        tem = dht11.temperature()
        hum = dht11.humidity()
        timestamp = time.localtime()
        timestamp = changeByTimezone(timestamp)
        writeToData(tem, hum, timestamp, is_valid)
    except:
        print("ERROR loading data from DHT in 'readDataFromSensors'")

# Non-blocking pump control
pump_running = False
pump_end_ms = 0

def start_pump(seconds):
    global pump_running, pump_end_ms
    motor_a.value(1)
    motor_b.value(0)
    pump_running = True
    pump_end_ms = time.ticks_add(time.ticks_ms(), int(seconds * 1000))
    print("pump started")

def stop_pump():
    global pump_running
    motor_a.value(0)
    motor_b.value(0)
    pump_running = False
    print("pump stopped")

# LED helpers (stateless outputs)
def led_off():
    led_r.value(0)
    led_g.value(0)
    led_b.value(0)

def led_normal():
    led_r.value(1)
    led_g.value(1)
    led_b.value(1)

# Non-blocking party mode (stepper)
party_step = 0
last_led_change_ms = time.ticks_ms()
LED_INTERVAL_MS = 200

def led_party_step():
    global party_step, last_led_change_ms
    now = time.ticks_ms()
    if time.ticks_diff(now, last_led_change_ms) >= LED_INTERVAL_MS:
        last_led_change_ms = now
        # cycle: R -> G -> B
        if party_step == 0:
            led_r.value(1); led_g.value(0); led_b.value(0)
        elif party_step == 1:
            led_r.value(0); led_g.value(1); led_b.value(0)
        elif party_step == 2:
            led_r.value(0); led_g.value(0); led_b.value(1)
        party_step = (party_step + 1) % 3

# ---------------- BUTTON EDGE + DEBOUNCE ----------------
# store previous states for falling-edge detection
prev_water = BTN_WATER.value()
prev_display = BTN_DISPLAY.value()
prev_mode = BTN_MODE.value()
DEBOUNCE_MS = 200
last_water_ms = 0
last_display_ms = 0
last_mode_ms = 0

#####################################
# -----------MAIN LOOP --------------
#####################################
display_on = False
lights_on = False
party_mode = False
last_time = time.time()
DATA_INTERVAL = 600  # seconds
WATERING_TIME = 10  # seconds

# clear initial info after short wait
time.sleep(2)
oled.fill(0)
oled.show()


print(changeByTimezone(time.localtime()))

while True:
    now_ms = time.ticks_ms()

    # ---------------- update pump (non-blocking) ----------------
    if pump_running and time.ticks_diff(now_ms, pump_end_ms) >= 0:
        stop_pump()

    # ---------------- handle display ----------------
    if display_on:
        try:
            dht11.measure()
            tem = dht11.temperature()
            hum = dht11.humidity()
            oled.fill(0)
            oled.text("Temp: {} C".format(tem), 0, 16)
            oled.text("Hum:  {} %".format(hum), 0, 32)
            oled.show()
        except:
            continue
        #     oled.fill(0)
        #     oled.text("Sensor ERR", 0, 24)
        #     oled.show()

    # ---------------- LED behavior (non-blocking) ----------------
    if lights_on:
        if party_mode:
            led_party_step()   # non-blocking periodic step
        else:
            led_normal()
    else:
        led_off()

    # ---------------- periodic sensor logging ----------------
    curr_time = time.time()
    if curr_time - last_time >= DATA_INTERVAL:
        readDataFromSensors(DATE_IS_SET)
        last_time = curr_time

    # ---------------- read buttons with falling-edge + debounce ----------------
    cur_water = BTN_WATER.value()
    if prev_water == 1 and cur_water == 0:
        if time.ticks_diff(now_ms, last_water_ms) > DEBOUNCE_MS:
            # start pump (non-blocking)
            start_pump(WATERING_TIME)
            last_water_ms = now_ms
    prev_water = cur_water

    cur_display = BTN_DISPLAY.value()
    if prev_display == 1 and cur_display == 0:
        if time.ticks_diff(now_ms, last_display_ms) > DEBOUNCE_MS:
            display_on = not display_on
            lights_on = display_on
            if display_on:
                print("display is on; lights on")
            else:
                print("display is off; lights off")
                oled.fill(0)
                oled.show()
            last_display_ms = now_ms
    prev_display = cur_display

    cur_mode = BTN_MODE.value()
    if prev_mode == 1 and cur_mode == 0:
        if time.ticks_diff(now_ms, last_mode_ms) > DEBOUNCE_MS:
            # toggle mode only if lights are on (same behavior as original)
            if lights_on:
                party_mode = not party_mode
                print("party mode" if party_mode else "normal mode")
            last_mode_ms = now_ms
    prev_mode = cur_mode

    # small main loop delay (keeps responsiveness and reduces CPU)
    time.sleep(0.02)
