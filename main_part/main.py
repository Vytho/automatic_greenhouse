from display_init import SSD1306_I2C
import machine
import time

# ---------- Konfigurácia I2C ----------
# Použijeme I2C(0) so SDA=GP0, SCL=GP1
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# sken adres
print("I2C scan:", i2c.scan())

# Správna adresa bežne 0x3C alebo 0x3D. Ak scan vráti [], skontroluj zapojenie.
addrs = i2c.scan()
if not addrs:
    # let this print statement here
    # will be used as log message 
    print("OLED alebo I2C sa nenašlo. Skontroluj zapojenie a napájanie (3.3V).")
else:
    addr = addrs[0]
    print("Použijem adresu 0x{:02X}".format(addr))
    # vytvor SSD1306 inštanciu (128x64)
    oled = SSD1306_I2C(128, 64, i2c, addr=addr)

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







