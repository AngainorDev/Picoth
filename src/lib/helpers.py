import time

# map a numeric touch to the keypad touch index
NUMPAD_TO_TOUCH = [13, 8, 9, 10, 4, 5, 6, 0, 1, 2]

# map a keypad touch index to a numpad int or string.
TOUCH_TO_NUMPAD = [7, 8, 9, "L", 4, 5, 6, "+", 1, 2, 3, "-", "P", 0, "N", "E"]


def hex_to_rgb(hex_str):
    return [int(hex_str[x:x + 2], 16) for x in (0, 2, 4)]


def ts_to_unix(dt, offset=-3600):
    return time.mktime(dt) + offset


def state_to_button(state):
    # From state int, gives the first button down
    # Does not detect multiple buttons
    for i in range(16):
        if state & (1 << i):
            return i
    return -1


def button_to_numpad(button):
    return TOUCH_TO_NUMPAD[button]

