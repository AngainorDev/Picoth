# Picoth
An OTP enabled macro keyboard based upon a Raspberry Pi Pico and RGB keypad base from Pimoroni.

![Preview](https://pbs.twimg.com/media/ExEwmVaXMAUbIDw?format=png&name=small)

Project log on Hackaday.io: [Picoth on HackaDay.io](https://hackaday.io/project/177593-picoth-2fa-auth-with-pi-pico)

**Warning**: In its current state, this device is not safe to use in an adversarial environment: anyone having access to it could steal your config file, hence your OTP keys.    
Next versions will include encrypted keys and an option to remove the USB disk drive mount. 

# Overview

This is a work in progress, feel free to ask and request more info.  
[Twitter @Angainor15](https://twitter.com/Angainor15)  
[Discord](https://discord.gg/gy9xpuQK8A)


## keypad mapping

The mapping is a regular keypad instead of the Pimoroni default's one.

|||||  
|---|---|---|---|  
| 7 | 8 | 9 | L |  
| 4 | 5 | 6 | + |  
| 1 | 2 | 3 | - |  
| P | 0 | N | E |

L = Sleep/Lock  
E = Enter  
P = Previous Page  
N = Next Page  

# Hardware

- 1× Raspberry Pi Pico  
https://shop.pimoroni.com/products/raspberry-pi-pico
- 1× Pimoroni's RGB Keypad  
https://shop.pimoroni.com/products/pico-rgb-keypad-base
- 1× Pimoroni's Pico display  
https://shop.pimoroni.com/products/pico-display-pack
- 1× DS3231 Arduino module  
https://s.click.aliexpress.com/e/_AZGRXo

*Note:* This is not sponsored by Pimoroni, I was not paid to build this project and bought the hardware myself.  
I just like what the pirates do.

# Setup

See the wiring and photos on [Hackaday](https://hackaday.io/project/177593-picoth-2fa-auth-with-pi-pico/log/189173-definitive-wiring)
 and [Twitter post](https://twitter.com/Angainor15/status/1359431057611882498) 


## Circuit python

https://circuitpython.org/board/raspberry_pi_pico/  
I was running on 6.2.0 Beta 3, Beta 4 is now available.

## Circuit Python libraries

All needed libs are duplicated in the src/lib for convenience.  
Just copy the "src/lib" content on your CIRCUITPY usb drive.

For reference, here are the stock Adafruit libs that were used (they can all be found in the default [Adafruit lib pack](https://github.com/adafruit/Adafruit_CircuitPython_Bundle))  
  
- adafruit_display_text
- adafruit_hashlib
- adafruit_hid
- adafruit_register
- adafruit_dotstar
- adafruit_ds3231
- adafruit_progressbar
- adafruit_st7789

The RGBKeypad library is very heavily inspired from Sandy J Mac Donald's awesome Keybow 2040 library  
https://twitter.com/sandyjmacdonald/status/1370459658608074758  
https://github.com/sandyjmacdonald/keybow2040-circuitpython

## Source code

Just copy the python files from the "src/" folder on your CIRCUITPY usb drive.  

*Note:* Nothing is "clean" yet. It's a working but proof of concept code, iterated from several attempts and migration from MP to CP and libraries changes.  
This will be improved over time.  

## Time config

The RTC module needs to be setup once.  
This will eventually be done via the GUI, but in the mean time you can do it manually from the Python repl:

Init a DS3231 instance:  
```
from adafruit_ds3231 import DS3231
import board
import busio
import time
i2c = busio.I2C(board.GP11, board.GP10)
ds = DS3231(i2c)
```

From there you can query the current datetime:  
`ds.datetime`  
the temp  
`ds.temperature`  

and more importantly setup the date and time:  
`rtc.datetime = time.struct_time((2021, 3, 24, 15, 3, 0, 0, -1, -1))`    
params are year, month, day, hour, min, sec, weekday(0-6), yearday(can be -1), isdst(-1 or 0)

# Config

Copy params.sample.json to params.json, edit and copy on your device.

params.json is a json file.  
Core params are
```
{
  "check": "ff00112233",
  "layout": "fr",
  "time_offset": -3600,
  "pages":[]
}
```

- check is reserved for future use when encrypting the keys 
- layout is the keyboard layout (currently supports "us" and "fr")
- time_offset - in seconds - is your timezone: -3600 for GMT+1
- pages is a list of pages (1 page minimum has to be defined)

Every page is defined as:  

```
 {"type": "TOTP",
     "name": "Test OTPs",
     "keys": [
       ["","000000",""],
       ["qTrade","FF7829","ftslvgd2zddprptn"],
       ["Bittrex","0081EB","stflvgd2zddprptn"],
       ["Nash.io","5790FF","ltfsvgd2zddprptn"],
       ["Github","F34F29","vtfslgd2zddprptn"],
       ["","000000",""],
       ["","000000",""],
       ["Discord","4285F4","fslvgd2zddprptnt"],
       ["","000000",""],
       ["","000000",""]
       ]
    },

```

- type: only "TOTP" is supported for now
- keys: a list [0..9] of entries. See layout above, fits a numpad, that is first entry, 0, is on the lower line, and 7, 8, 9 (3 last entries in the list) are the 3 top keys.
- Each key is a list as well: ["label", "hexcolor", "totp seed"]
- Use ["","000000",""] for an inactive key
 
 
# Roadmap

- Keys encryption, device lock, pincode
- More modes (type in password or text, media pad, pomodoro)
- Sleep/screen saver mode
- Improve screen refresh speed
- Improve GUI
- 3D Printed case
- Alternate screens or no screen?


# Licence

Custom code is released under the GNU AFFERO GENERAL PUBLIC LICENSE.  
If this conflicts with some of the MIT licenced source code used, then the MIT licence is to be used instead.  
Specific code files can ship with their own licence in their header.
