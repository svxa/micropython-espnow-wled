# WLED Micropython control button script
# This script is designed to be used with a M5Stack Atom S3 Lite and a WLED device based on a 0.15.0 or later version.
# The Atom S3 Lite has a button on GPIO 41 and a single RGB LED on GPIO 35.

import espnow
from machine import Pin, Timer
import neopixel
import network
import time

# ----------------- Constants -----------------

# PEER: Either the MAC address (form: b"\xaa\xbb\xcc\xdd\xee\xff") of the WLED device or None/False for broadcast
# WIFI_CHANNEL: 0 for all channels, 1-14 for specific channel
# BUTTON_NUMBER_PRESET: Button number to send to WLED device
# BUTTON_NUMBER_OFF: Button number to turn off the light
# DEBOUNCE_BUTTON: Debounce time for button press
# RGB_OFF_TIMOUT: Time to turn off RGB after button press
# DEBOUNCE_OFF: Time after which button press will turn off the light instead of sending a regular button press
# SEND_ON_AFTER: Time after which button press will send a regular button press instead of turning off the light
# FLASH_AFTER_SETUP: Flash the LED twice after setup is complete

PEER = b"\xff\xff\xff\xff\xff\xff" # Broadcast address; change to your WLED controller's MAC or leave as is
WIFI_CHANNEL = 0
BUTTON_NUMBER_PRESET = 20
BUTTON_NUMBER_OFF = 2
DEBOUNCE_BUTTON = 250
RGB_OFF_TIMOUT = 2000  # Recommended to set it equal to DEBOUNCE_OFF
DEBOUNCE_OFF = 2000
SEND_ON_AFTER = 10000
FLASH_AFTER_SETUP = True

# Note that the Wizmote preset buttons always reset the night light timer!
# If you want to use the night light, enter it in your presets and use a non-Wizmote button number!

# How to use a non-Wizmote button number in WLED:
# Go to http://wled_ip/edit
# Upload the file `remote.json` with the following contents:
# ```json
# {
#   "20": {
#     "label": "CyclePresets",
#     "cmd": "P1=1&P2=3&PL=~"
#   }
# }
# ```
# This will make the button `20` cycle through presets 1-3.
# You can change the presets by changing `P1=1&P2=3` to `P1=1&P2=4` for presets 1-4, etc.
# PL=~ will cycle through the presets in increasing order.
# See the WLED documentation for the HTTP API for more information on the cmd parameter.
# Using the `remote.json` requires at least version 0.15 or so of WLED.
# Tested on WLED_0.15.0-b4_ESP32_audioreactive.bin


# ----------------- Functions -----------------
def wifi_reset():  # Reset wifi to AP_IF off, STA_IF on and disconnected
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    sta.active(True)
    while not sta.active():
        time.sleep(0.01)
    sta.disconnect()  # For ESP8266
    while sta.isconnected():
        time.sleep(0.01)
    return sta, ap


def change_channel(channel):
    sta.config(channel=channel)


def build_msg(button):
    global seq
    seq += 1
    message = bytearray(13)
    message[0] = 0x81 if button != 1 else 0x91
    message[1] = seq & 0xFF
    message[2] = (seq >> 8) & 0xFF
    message[3] = (seq >> 16) & 0xFF
    message[4] = (seq >> 24) & 0xFF
    message[5] = 0x20
    message[6] = button
    message[7] = 0x01
    message[8] = 0x64
    return message


def send(button):
    msg = build_msg(button)
    if WIFI_CHANNEL != 0:
        if not e.send(PEER, msg, False):
            print("Failed to send")
    else:
        original_channel = sta.config("channel")
        for i in range(1, 14):
            change_channel(i)
            time.sleep(0.01)
            if not e.send(PEER, msg, False):
                print("Failed to send")
        change_channel(original_channel)


def init_led(color=None, duration=RGB_OFF_TIMOUT):
    if color is not None:
        set_color(color)
    led_timer.init(period=duration, mode=Timer.ONE_SHOT, callback=led_off)


def set_color(color):
    led[0] = color
    led.write()


def send_cycle_preset():
    send(BUTTON_NUMBER_PRESET)
    init_led(color_on)


def send_light_off():
    send(BUTTON_NUMBER_OFF)
    init_led(color_off)


def led_off(timer):
    timer.deinit()
    _on = sum(led[0]) > 0
    if _on:
        set_color((0, 0, 0))


def callback(p):
    global last_button_press
    tdiff = time.ticks_ms() - last_button_press
    last_button_press = time.ticks_ms()
    if tdiff < DEBOUNCE_BUTTON:
        return
    if (tdiff < SEND_ON_AFTER) & (tdiff > DEBOUNCE_OFF):
        send_light_off()
    else:
        send_cycle_preset()


# ----------------- Setup -----------------
# Initialize sequence number
# Sequence number does not really matter, except that it must be unique for each message
seq = 1

# WIZMOTE_BUTTON_ON          1
# WIZMOTE_BUTTON_OFF         2
# WIZMOTE_BUTTON_NIGHT       3
# WIZMOTE_BUTTON_ONE         16
# WIZMOTE_BUTTON_TWO         17
# WIZMOTE_BUTTON_THREE       18
# WIZMOTE_BUTTON_FOUR        19
# WIZMOTE_BUTTON_BRIGHT_UP   9
# WIZMOTE_BUTTON_BRIGHT_DOWN 8

# Set up physical button
btn = Pin(41, Pin.IN)
# Ensure the first button press after boot is always considered a turn on command
last_button_press = -max(DEBOUNCE_BUTTON, DEBOUNCE_OFF, SEND_ON_AFTER)

# Set up LED
led_pin = Pin(35, Pin.OUT)
led_timer = Timer(0)
led = neopixel.NeoPixel(led_pin, 1)
color_on = (0, 15, 0)
color_off = (15, 0, 0)


# Set up WiFi
_WIFI_CHANNEL = WIFI_CHANNEL if 1 <= WIFI_CHANNEL <= 14 else 1
sta, ap = wifi_reset()
sta.config(channel=_WIFI_CHANNEL)

# Set up ESP-NOW
if not PEER:
    PEER = b"\xff" * 6  # All peers (broadcast)
e = espnow.ESPNow()
e.active(True)
e.add_peer(PEER)

# Set up button interrupt
btn.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Flash twice to indicate setup is complete
flash_duration = 250
n_flashes = 2
if FLASH_AFTER_SETUP is True:
    for i in range(2):
        init_led((0, 0, 15), duration=flash_duration)
        if i < n_flashes - 1:
            time.sleep(flash_duration * 2 / 1000)
