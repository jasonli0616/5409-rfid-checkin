from RPLCD import CharLCD
import RPi.GPIO as GPIO
import os

use_lcd = True

lcd = None
if use_lcd:
    lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

def write_text(text):
    if use_lcd:
        lcd.write_string(text)
    else:
        print(f"{text}\n")


def clear_text():
    if use_lcd:
        lcd.clear()
    else:
        os.system("clear")