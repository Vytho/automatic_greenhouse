from display_init import SSD1306_I2C
import machine
import time
from machine import Pin

# ---------------------------------------
# BUTTONS CONFIGURATION
# ---------------------------------------
    # assuming pulled-up, so pressed = LOW
    # button 1 – manual watering --> GP0
    # button 2 – display + lights --> GP1
    # button 3 – change light mode --> GP2
BTN_WATER = Pin(0, Pin.IN, Pin.PULL_UP)
BTN_DISPLAY = Pin(1, Pin.IN, Pin.PULL_UP)
BTN_MODE = Pin(2, Pin.IN, Pin.PULL_UP) 


# ---------------------------------------
# I2C CONFIGURATION
# ---------------------------------------
    # SDA --> GP3
    # SCL --> GP4
i2c = machine.I2C(0, sda=machine.Pin(3), scl=machine.Pin(4), freq=400000)

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




















#  _________This is used fro lcd display DO NOT REMOVE_________
# # ---------- Konfigurácia I2C ----------
# # Použijeme I2C(0) so SDA=GP0, SCL=GP1
# i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# # sken adres
# print("I2C scan:", i2c.scan())

# # Správna adresa bežne 0x3C alebo 0x3D. Ak scan vráti [], skontroluj zapojenie.
# addrs = i2c.scan()
# if not addrs:
#     # let this print statement here
#     # will be used as log message 
#     print("OLED alebo I2C sa nenašlo. Skontroluj zapojenie a napájanie (3.3V).")
# else:
#     addr = addrs[0]
#     print("Použijem adresu 0x{:02X}".format(addr))
#     # vytvor SSD1306 inštanciu (128x64)
#     oled = SSD1306_I2C(128, 64, i2c, addr=addr)

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




# States
display_on = False
lights_on = False
party_mode = False

while True:
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







