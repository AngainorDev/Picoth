"""
Main Picoth manager
"""


import time
import busio
import board
from adafruit_ds3231 import DS3231

from totp import TOTP
from rgbkeypad import RgbKeypad

import usb_hid
from adafruit_hid.keyboard import Keyboard

from helpers import hex_to_rgb, ts_to_unix, NUMPAD_TO_TOUCH, button_to_numpad
import pico_dio


class Picoth(object):

    def __init__(self, config):
        """
        Init and binds the H/W
        """
        # Pimoroni's RGB Keypad - Default wiring
        self.KEYPAD = RgbKeypad()
        self.KEYS = self.KEYPAD.keys
        # DS3231 module, i2c1, SCL=GP11 and SDA=GP10
        i2c = busio.I2C(board.GP11, board.GP10)
        self.DS = DS3231(i2c)
        print(self.DS.datetime)  # Just to check time at boot when dev

        self.CONFIG = config

        # USB HID
        keyboard = Keyboard(usb_hid.devices)
        if self.CONFIG.get("layout", "us") == "fr":
            # More to come
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            self.LAYOUT = KeyboardLayoutFR(keyboard)
        else:
            # Default US layout
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            self.LAYOUT = KeyboardLayoutUS(keyboard)

        # Pico display
        self.DISPLAY = pico_dio.get_display()
        self.SCREENS = dict()
        self.SCREENS["splash"] = pico_dio.get_splash()

        self.DISPLAY.show(self.SCREENS["splash"])

        self.UPDATE_INDEX = 0
        self.LOCKED = False
        self.LAST_CODE = ""
        self.OTP = None
        self.MODE = 0
        self.PAGE = 0
        self.INDEX = None
        self.LAST_COUNTER = 0  # time // 30, OTP counter

        self.SCREENS["OTP"] = pico_dio.get_otp_group()
        self.SCREENS["PAGE"] = pico_dio.get_page_group()

        self.display_page(self.PAGE)

        for key in self.KEYS:
            @self.KEYPAD.on_press(key)
            def press_handler(a_key):
                self.handle_numpad(button_to_numpad(a_key.number))

    def run(self):
        self.KEYS[15].set_led(0, 100, 100)  # heartbeat
        time_last_fired = [0, 0]
        while True:
            self.KEYPAD.update()
            tm = time.monotonic()
            if tm - time_last_fired[1] > 0.1:
                self.update()
                time_last_fired[1] = tm
            if tm - time_last_fired[0] > 1.0:
                # print("update", time_last_fired)
                time_last_fired[0] = tm
                self.KEYS[15].toggle_led()

    def display_page(self, page):
        self.OTP = None
        self.LAST_COUNTER = 0
        self.PAGE = page
        self.INDEX = None
        self.KEYPAD.clear_all()
        for i, item in enumerate(self.CONFIG["pages"][self.PAGE]["keys"]):
            r, g, b = hex_to_rgb(item[1])
            self.KEYS[NUMPAD_TO_TOUCH[i]].set_led(r, g, b)
        # TODO: generalize this key behaviour
        self.KEYS[15].set_led(0, 100, 100)  # cyan = heartbeat
        self.DISPLAY.auto_refresh = False
        # TODO: auto center
        self.SCREENS["PAGE"][1].text = " Mode {}".format(self.CONFIG["pages"][self.PAGE]["type"])
        self.SCREENS["PAGE"][2].text = "Page {}".format(self.PAGE)
        self.SCREENS["PAGE"][3].text = self.CONFIG["pages"][self.PAGE]["name"]
        self.DISPLAY.show(self.SCREENS["PAGE"][0])
        self.DISPLAY.auto_refresh = True

    def handle_numpad(self, numpad):
        # numpad int or char
        # print("handle numpad", PAGE, numpad)
        if self.MODE == 0:
            # User mode
            if type(numpad) == int:
                key = self.CONFIG["pages"][self.PAGE]["keys"][numpad][2]
                if key != '':
                    # dup code
                    for i, item in enumerate(self.CONFIG["pages"][self.PAGE]["keys"]):
                        r, g, b = hex_to_rgb(item[1])
                        self.KEYPAD.set_led(NUMPAD_TO_TOUCH[i], r, g, b)
                    self.INDEX = numpad
                    if self.CONFIG["pages"][self.PAGE]["type"] == "TOTP":
                        self.OTP = TOTP(key)
                        self.KEYS[15].set_led(0, 100, 0)  # green = enter
                        self.LAST_CODE = ""
                        self.LAST_COUNTER = 0
                        self.DISPLAY.auto_refresh = False
                        # TODO: auto center
                        self.SCREENS["OTP"][2].text = self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][0]
                        self.SCREENS["OTP"][2].color = int(self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][1], 16)
                        self.SCREENS["OTP"][1].text = "------"
                        self.DISPLAY.show(self.SCREENS["OTP"][0])
                        self.DISPLAY.auto_refresh = True
                    elif self.CONFIG["pages"][self.PAGE]["type"] == "KEYS":
                        self.KEYS[15].set_led(0, 100, 0)  # green = enter
                        self.DISPLAY.auto_refresh = False
                        # TODO: auto center
                        self.SCREENS["OTP"][2].text = self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][0]
                        self.SCREENS["OTP"][2].color = int(self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][1], 16)
                        self.SCREENS["OTP"][1].text = ""
                        self.SCREENS["OTP"][3].progress = 1.0
                        self.DISPLAY.show(self.SCREENS["OTP"][0])
                        self.DISPLAY.auto_refresh = True
                else:
                    self.OTP = None
            elif numpad == "N":
                self.PAGE += 1
                if self.PAGE >= len(self.CONFIG["pages"]):
                    self.PAGE = 0
                self.display_page(self.PAGE)
            elif numpad == "P":
                self.PAGE -= 1
                if self.PAGE < 0:
                    self.PAGE = len(self.CONFIG["pages"]) - 1
                self.display_page(self.PAGE)
            elif numpad == "E":
                if self.OTP and self.CONFIG["pages"][self.PAGE]["type"] == "TOTP":
                    self.LAYOUT.write(self.LAST_CODE)
                if self.CONFIG["pages"][self.PAGE]["type"] == "KEYS":
                    self.LAYOUT.write(self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][2])

    def update(self):
        self.UPDATE_INDEX += 1
        if self.UPDATE_INDEX > 100:
            self.UPDATE_INDEX = 0
        if self.LOCKED:
            return
        if self.MODE == 0:
            # User mode
            if self.CONFIG["pages"][self.PAGE]["type"] == "TOTP":
                self.update_totp()
            if self.CONFIG["pages"][self.PAGE]["type"] == "KEYS":
                self.update_keys()

    def update_totp(self):
        if self.OTP is None:
            # print("No OTP")
            return
        try:
            color = self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][1]
            r, g, b = hex_to_rgb(color)
            if self.UPDATE_INDEX % 3 == 0:
                self.KEYPAD.set_led(NUMPAD_TO_TOUCH[self.INDEX], 0, 0, 0)
            else:
                self.KEYPAD.set_led(NUMPAD_TO_TOUCH[self.INDEX], r, g, b)
            # TODO: offset in config
            t = ts_to_unix(self.DS.datetime, offset=self.CONFIG["time_offset"])
            color = 0x00fa00
            left, counter = self.OTP.time_left(t)
            if left < 10:
                color = 0xfafa00
            if left < 5:
                color = 0xfa0000
            # Todo: only update if width change?
            # self.SCREENS["OTP"][3].width = left * 240 // 30
            # Have to access the protected member since the lib does only allow color definition at init time
            self.SCREENS["OTP"][3]._palette[2] = color
            self.SCREENS["OTP"][3].progress = left / 30
            if counter != self.LAST_COUNTER and self.OTP:
                # Only update code on screen screen (slow) if changed
                self.LAST_COUNTER = counter
                code = self.OTP.totpt(t)  # 0.22sec!
                self.LAST_CODE = code
                self.SCREENS["OTP"][1].text = code
            if self.OTP:
                # Debug
                if self.UPDATE_INDEX % 10 == 0:
                    print(self.LAST_CODE)

        except Exception as e:
            print(e)
            pass

    def update_keys(self):
        try:
            color = self.CONFIG["pages"][self.PAGE]["keys"][self.INDEX][1]
            # TODO1: move hex conversion in KEYPAD
            # TODO2: refactor/factorize common behaviour of the blinking active keys
            r, g, b = hex_to_rgb(color)
            if self.UPDATE_INDEX % 3 == 0:
                self.KEYPAD.set_led(NUMPAD_TO_TOUCH[self.INDEX], 0, 0, 0)
            else:
                self.KEYPAD.set_led(NUMPAD_TO_TOUCH[self.INDEX], r, g, b)
        except Exception as e:
            print(e)
            pass
