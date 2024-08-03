# Micropython ESP-NOW WLED controller
This script is designed to be used with a M5Stack Atom S3 Lite and a WLED device based on a 0.15.0 or later version.
It was tested with WLED_0.15.0-b4_ESP32_audioreactive.bin from WLED.
The button allows you to turn on presets, cycle through them and turn off the WLED light.

If your presets do not activate night mode and you only want a single preset to be set, you can skip the `remote.json` and just change `BUTTON_NUMBER_PRESET` to 16 (preset 1), 17 (preset 2), 18 (preset 3), 19 (preset 4).

## Usage
### Turning the light on
To turn on the WLED light, press the button once. The button lights up in green to indicate an on signal being sent.

### Cycling through the presets
To cycle through the presets, press the button again within 2 seconds to go to the next preset. You can do that as often as you want.

### Turning the light off
To turn off the light, wait until the green light turns off (after 2 seconds). A button press now will turn off the light. The button will light up in red to indicate an off signal being sent.
If you wait longer than 10 seconds after the last press, the button will send an "on" signal again.
If you want to turn off the light after not having pressed the button for a while, you will need to press it twice: Press to cycle to the next preset, wait 2 seconds, press again to turn off.

## Setup
### Hardware
- M5Stack Atom S3 Lite
- WLED controller running 0.15.0 or higher
- Laptop, USB cables, etc.

### Software
- Micropython for the [Generic S3](https://micropython.org/download/ESP32_GENERIC_S3/)
  - Tested with version: `ESP32_GENERIC_S3-20240602-v1.23.0.bin`
  - Flashed to the ESP as described on the Micropython website
- I used Thonny IDE to copy the Python code to the Atom S3 Lite

### Installation
- Flash your Atom S3 Lite with Micropython
- Load the `main.py` from this repository in Thonny
- Edit the file with your MAC address / router channel / other preferences as described in `Configuration options` below
- Upload the file as `main.py` to your Atom S3 Lite
- Go to your WLED IP -> Config -> Wifi (http://wled_ip/settings/wifi)
- Scroll all the way down to `ESP-NOW Wireless`
- Activate `Enable ESP-NOW`. You might need to restart your WLED controller afterwards. You can to that by navigating to `http://wled_ip/reset`
- Now press the button on the Atom S3 Lite. Its MAC should now show up under `Last device seen` in the ESP-NOW section on WLED.
- Copy the MAC to `Paired Remote MAC`. Note that the MAC is all lowercase and without separators (like so aabbccddeeff)
- Navigate to `http://wled_ip/edit`; Click `Choose file` in the top left corner; select the `remote.json` from this repository; Upload the file.
- Click on the file in the file explorer on the left. You can now adjust it to match your number of presets, or change the executed command; See the [HTTP API documentation of WLED](https://kno.wled.ge/interfaces/http-api/) for more details.

## Configuration options
- PEER: Either the MAC address (form: b"\xaa\xbb\xcc\xdd\xee\xff") of the WLED device or None/False for broadcast
- WIFI_CHANNEL: 0 for all channels, 1-14 for a specific channel
- BUTTON_NUMBER_PRESET: Button number to send to WLED device. This needs to match either a valid WizMote button number or one specified in `remote.json`
- BUTTON_NUMBER_OFF: Button number to turn off the light
- DEBOUNCE_BUTTON: Debounce time for button press
- RGB_OFF_TIMOUT: Time to turn off RGB after button press
- DEBOUNCE_OFF: Time after which button press will turn off the light instead of sending a regular button press
- SEND_ON_AFTER: Time after which button press will send a regular button press instead of turning off the light
- FLASH_AFTER_SETUP: Flash the LED twice after startup is complete

## Note on night light (timer) mode
In the remote code of the WLED controller, any WizMote button press is followed by a turning off of the night light.
See `resetNightMode()` in [this line](https://github.com/Aircoookie/WLED/blob/3615ab535b3ebfb77a175a4cb2949d0a4a516143/wled00/remote.cpp#L157).
Thus, it is impossible to set a preset, which has night mode activated to the buttons 1-4 of the WizMote presets.

This is the reason why I chose to use an imaginary button `20` for the default button sent, so I could cycle through presets that have night mode activated.

## Credits
- https://github.com/Aircoookie/WLED/blob/main/wled00/remote.cpp
- https://wled.discourse.group/t/generic-esp32-espnow-remote-new-protocol-any-comments
- https://docs.micropython.org/en/latest/library/espnow.html
- https://github.com/insane2subro/ESPNOW2MQTT
