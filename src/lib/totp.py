"""
Extended from https://github.com/susam/mintotp/blob/master/mintotp.py
Adapted for Circuit Python, using adafruit libs when available

Licence: MIT
Copyright (c) 2019 Susam Pal
Copyright (c) 2021 Angainor Dev
"""

import base32
import hmac
import struct
import time
from adafruit_hashlib import sha1 as SHA1


class TOTP:

    __slots__ = ("_key", "_binkey", "time_step", "digits", "digest")

    def __init__(self, key, time_step=30, digits=6, digest=SHA1):
        self._key = key
        self._binkey = base32.b32decode(self._key.upper() + "=" * ((8 - len(self._key)) % 8))
        self.time_step = time_step
        self.digits = digits
        self.digest = digest

    def hotp(self, counter):
        # t = time.monotonic_ns()
        counter = struct.pack(">Q", counter)
        mac = hmac.new(self._binkey, counter, self.digest).digest()
        offset = mac[-1] & 0x0F
        binary = struct.unpack(">L", mac[offset: offset + 4])[0] & 0x7FFFFFFF
        """res = str(binary)[-self.digits:]
        while len(res) < self.digits:
            res = "0" + res
        """
        res = f"{binary:06d}"[-self.digits:]  # shorter, no speed diff
        # print("hotp", (time.monotonic_ns() - t)/ 1e9)  # 0.22 sec from .py, same from mpy
        return res

    def totp(self, margin=1.5):
        left, _ = self.time_left()
        while left < margin or left > self.time_step - margin:
            time.sleep(1)
            left = self.time_left()
            # print("left", left)
        return self.hotp(time.time() // self.time_step)

    def totpt(self, t):
        return self.hotp(t // self.time_step)

    def time_left(self, t=0):
        if t == 0:
            t = int(time.time())
        counter = t // self.time_step
        return self.time_step - t + self.time_step * counter, counter
