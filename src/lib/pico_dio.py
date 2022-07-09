import displayio
import board
import busio
import terminalio
from adafruit_display_text import label
# from adafruit_display_shapes import rect
from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)
from adafruit_st7789 import ST7789


# TODO: Refactor as a class so can be abstracted and use alternates screens or lower level lib when needed.

def get_display():
    displayio.release_displays()

    tft_cs = board.GP21
    tft_dc = board.GP16
    # tft_res = board.GP23
    spi_mosi = board.GP27
    spi_clk = board.GP26
    # https://gist.github.com/wildestpixel/86ac1063bc456213f92972fcd7c7c2e1
    spi = busio.SPI(spi_clk, MOSI=spi_mosi)
    while not spi.try_lock():
        pass
    # Configure SPI was 24MHz by default - Trying 64Mhz, no visible change
    spi.configure(baudrate=64000000)
    spi.unlock()
    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, baudrate=64000000)
    display = ST7789(display_bus, width=135, height=240, rowstart=40, colstart=53)
    display.rotation = 270
    return display


def get_splash():
    splash = displayio.Group()
    text_group2 = displayio.Group(scale=3, x=40, y=20)
    text2 = "Picoth"
    text_area2 = label.Label(terminalio.FONT, text=text2, color=0x00FF00)
    text_group2.append(text_area2)
    splash.append(text_group2)
    return splash


# OTP screen
def get_otp_group():
    otp_group = displayio.Group(scale=1, x=0, y=0)
    # OTP Code
    text_group1 = displayio.Group(scale=6, x=15, y=100)
    text1 = "999999"
    text_area1 = label.Label(terminalio.FONT, text=text1, color=0x00FF00)
    text_group1.append(text_area1)  # Subgroup for text scaling
    otp_group.append(text_group1)
    # OTP label
    text_group2 = displayio.Group(scale=3, x=40, y=20)
    text2 = "OTP Label"
    text_area2 = label.Label(terminalio.FONT, text=text2, color=0xFF0000)
    text_group2.append(text_area2)
    otp_group.append(text_group2)
    """
    # 2 rectangles seemed to fit, but adjusting their width afterward does not refresh the display.
    # grey rectangle
    rect1 = rect.Rect(0, 70, 240, 4, fill=0x1e1e1e)
    otp_group.append(rect1)
    # time left
    rect2 = rect.Rect(0, 70, 120, 4, fill=0x00fa00)
    otp_group.append(rect2)
    """
    progress = HorizontalProgressBar(
        (0, 60),
        (249, 9),
        outline_color=0x1e1e1e,
        bar_color=0x00fa00,
        direction=HorizontalFillDirection.LEFT_TO_RIGHT,
    )
    otp_group.append(progress)
    return otp_group, text_area1, text_area2, progress


def get_page_group():
    page_group = displayio.Group(scale=1, x=0, y=0)
    # Mode
    text_group1 = displayio.Group(scale=4, x=5, y=20)
    text_area1 = label.Label(terminalio.FONT, text="xx", color=0x00FF00)
    text_group1.append(text_area1)  # Subgroup for text scaling
    page_group.append(text_group1)
    # Page number
    text_group2 = displayio.Group(scale=3, x=70, y=70)
    text_area2 = label.Label(terminalio.FONT, text="Page X", color=0xFF0000)
    text_group2.append(text_area2)  # Subgroup for text scaling
    page_group.append(text_group2)
    # Label
    text_group3 = displayio.Group(scale=3, x=10, y=110)
    text_area3 = label.Label(terminalio.FONT, text="Label", color=0xFF0000)
    text_group3.append(text_area3)
    page_group.append(text_group3)
    return page_group, text_area1, text_area2, text_area3
