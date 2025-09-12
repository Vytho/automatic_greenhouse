# 🌱 MicroPython Smart Watering System 

**Short description**

A compact MicroPython project for a plant-watering controller running on a Raspberry Pi Pico W. It reads a DHT11 sensor, logs temperature/humidity to `data.txt`, shows status on an SSD1306 I2C OLED, controls a water pump (motor driver), and drives RGB LEDs and buttons for user interaction (display toggle, party mode, manual watering). 🚀

---

## ✨ Features

* I2C OLED status display (SSD1306) 🖥️
* Wi‑Fi connection and NTP time sync (if available) 📶⏰
* Local timezone conversion (CET/CEST) with DST handling for EU 🌍🕒
* Periodic logging of DHT11 sensor data to `data.txt` 🌡️💧
* Manual non‑blocking pump control (start/stop via button) 🚿🔁
* RGB LED normal & party modes
* Button debounce and falling-edge detection 🎛️

---

## 🔩 Hardware

* Raspberry Pi Pico / Pico W (or compatible board running MicroPython)
* SSD1306 128x64 OLED (I2C) 🖼️
* DHT11 temperature & humidity sensor 🌡️
* Motor driver / small DC pump 🛠️🚰
* RGB LEDs (3 pins) or single RGB LED with appropriate resistors 🔴🟢🔵
* 3 push buttons (pulled-up assumed) 🔘

### 🔌 Pin mapping (from project)

* **I2C (OLED)**: SDA → GP0, SCL → GP1
* **Buttons** (pulled-up, pressed = LOW)

  * Manual watering → GP6 🪴
  * Display + lights → GP7 💡
  * Change light mode → GP8 🎚️
* **DHT11 data** → GP9 🌡️
* **Motor driver**

  * motor\_a (B-1A) → GP15 ➡️
  * motor\_b (B-1B) → GP14 ⬅️
* **RGB LED**

  * Red → GP18 🔴
  * Green → GP19 🟢
  * Blue → GP20 🔵

> **Note**: Adjust pins to match your wiring. If you use PWM for LED brightness, swap the digital pins to PWM-capable pins and use `PWM`.

---

## 🧩 Software / Dependencies

* MicroPython firmware for your board
* `ssd1306` driver (in project, referenced as `display_init.SSD1306_I2C`) 📦
* `dht` module (part of MicroPython)
* `ntptime` module (part of MicroPython)
* `network` (for boards with Wi‑Fi, e.g. Pico W)

Make sure `display_init.py` (or an equivalent SSD1306 driver) is present in the filesystem.

---

## ⚙️ Configuration

Create a `password.txt` file in the board filesystem with two lines:

```
<SSID_NAME>
<SSID_PASSWORD>
```

The code will read the first two lines as Wi‑Fi name and password. If there is no Wi‑Fi or NTP is unreachable, the program continues and logs sensor data with a missing timestamp flag. ⚠️

---

## 🗂️ Files produced / data format

* `data.txt` — appended lines with either full timestamp or `-` if time isn't set.

If timestamp available:

```
YYYY-M-D H:M:S,temperature,humidity
```

If timestamp not available:

```
-,temperature,humidity
```

---

## ▶️ How to use

1. Copy `main.py`, `display_init.py`, and other modules to the board filesystem.
2. Create `password.txt` with your Wi‑Fi credentials (or leave it blank to run offline).
3. Power the board. The OLED shows initial power/Wi‑Fi status. 🔋
4. Use the **manual watering** button to run the pump for `WATERING_TIME` seconds. 🚿
5. Use **display** button to toggle the display + lights. 💡
6. Use **mode** button while lights are on to toggle party mode. 🎉

---

## 🧮 Important constants (in code)

* `DATA_INTERVAL` — how often sensor data is logged (seconds). Default: `600`.
* `WATERING_TIME` — how long the pump runs when manually triggered (seconds). Default: `10`.
* `TIMEOUT` — seconds to wait for Wi‑Fi connection before continuing without it. Default: `20`.

Adjust these in the source to fit your needs.

---

## 🛠️ Troubleshooting

* **OLED not detected**: run an I2C scan; ensure wiring and address. The project uses the first found I2C address; if you have multiple I2C devices, update the code to use the correct address. 🔎
* **Wi‑Fi does not connect**: check `password.txt` formatting and SSID name. The code will continue without Wi‑Fi after `TIMEOUT` seconds. 📡
* **NTP fails**: NTP may be blocked by network or router; code catches exceptions and continues with logs marked without timestamps. 🌐
* **DHT11 read fails when LEDs/Pump are ON**: some sensors are sensitive to electrical noise. If you observe failed DHT reads while the pump or LEDs are running, try:

  * Add a common ground and proper decoupling (capacitors) near motor and pump driver. 🧲
  * Put a small RC/snubber across the motor or use a flyback diode with motor driver. 🔧
  * Move DHT sensor wiring away from motor wires or add ferrite beads. 📏
  * Add short delay between turning on motor/LEDs and reading DHT. ⏳

---

## 🔭 Extending the project / TODOs

* Add 'automatic watering' feature ( using some time module would be ideal to avoid setting time everytime Pico is turned on ) 📆
* Implement PWM-based brightness control for RGB LED. 🔆
* Add web UI (for Pico W) to view sensor logs and manually trigger pump. ( data can be uploaded to Google sheets )🌐
* Persist configuration in a JSON file instead of `password.txt`. 🗃️
* Improve error handling and add an LED/error codes for easier debugging. 🐞

---

## 📝 License

This project is provided under the MIT License — feel free to reuse and adapt. 🧾

---

## 🤝 Contact / Contributing

If you want help adapting this README for another board or adding features, tell me which parts you want changed and I can update the document. 💬
