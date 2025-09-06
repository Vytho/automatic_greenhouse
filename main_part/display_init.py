# This file contains class that enables using OLED display
# main.py
# MicroPython pre Raspberry Pi Pico W + SSD1306 I2C 128x64


import framebuf

# zapojenie 
    # VCC → 3.3V (na Pico W; NIE 5V)

    # GND → GND

    # SDA → GP0 (GPIO0)

    # SCL → GP1 (GPIO1)


# ---------- SSD1306 driver (I2C) ----------
# minimalistická verzia ovládača založená na oficiálnom MicroPython ssd1306.py
# funguje pre 128x64 a 128x32

_CMD = 0x00
_DATA = 0x40

class SSD1306:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        # framebuf: MONO_VLSB ako v oficiálnom ovládači
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MVLSB)

    def poweroff(self): pass
    def poweron(self): pass
    def contrast(self, contrast): pass

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C):
        super().__init__(width, height)
        self.i2c = i2c
        self.addr = addr
        self.init_display()

    def write_cmd(self, cmd):
        # posiela jeden byte príkazu
        self.i2c.writeto(self.addr, bytes([_CMD, cmd]))

    def write_cmds(self, cmds):
        for c in cmds:
            self.write_cmd(c)

    def init_display(self):
        # inicializačná sekvencia (typická pre SSD1306)
        for cmd in (
            0xAE,         # display off
            0xD5, 0x80,   # set display clock div
            0xA8, self.height - 1, # multiplex
            0xD3, 0x00,   # display offset
            0x40,         # start line
            0x8D, 0x14,   # charge pump
            0x20, 0x00,   # memory mode
            0xA1,         # seg remap
            0xC8,         # com scan dec
            0xDA, 0x12,   # com pins
            0x81, 0xCF,   # contrast
            0xD9, 0xF1,   # precharge
            0xDB, 0x40,   # vcom detect
            0xA4,         # resume RAM
            0xA6,         # normal display
            0xAF):        # display on
            self.write_cmd(cmd)

        self.fill(0)
        self.show()

    def show(self):
        # zapíše celý buffer na displej (page addressing)
        for page in range(self.pages):
            self.write_cmd(0xB0 | page)   # set page address
            self.write_cmd(0x00)          # set low column addr
            self.write_cmd(0x10)          # set high column addr
            start = page * self.width
            end = start + self.width
            # posielame prefix 0x40 (data) + kуск dát
            # MicroPython I2C.writeto príjma bytes -> posielame v dvoch častiach ak treba
            self.i2c.writeto(self.addr, bytes([_DATA]) + self.buffer[start:end])

    # jednoduché framebuffer funkcie využívajú FrameBuffer API
    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def rect(self, x, y, w, h, col):
        self.framebuf.rect(x, y, w, h, col)

    def fill_rect(self, x, y, w, h, col):
        self.framebuf.fill_rect(x, y, w, h, col)


