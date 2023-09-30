from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import os

use_lcd = True

lcd = None
if use_lcd:
    lcd = CharLCD("PCF8574", 0x27, cols=16, rows=4)

def write_text(*text):
    if use_lcd:
        lcd.write_string("\r\n".join(text))
    print("\n".join(text) + "\n")


def clear_text():
    if use_lcd:
        lcd.clear()
    os.system("clear")