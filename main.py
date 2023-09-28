import binascii

from pn532pi import Pn532, pn532, Pn532I2c

import os
import integration
import lcdscreen

# Set up I2C
PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)


def setup():
    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if (not versiondata):
        lcdscreen.write_text("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    #  configure board to read RFID tags
    nfc.SAMConfig()

    # print("Waiting for an ISO14443A Card ...")
    lcdscreen.clear_text()
    lcdscreen.write_text("Ready to scan...")


def loop():
    #  Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    #  'uid' will be populated with the UID, and uidLength will indicate
    #  if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if (success):
        #  Display some basic information about the card
        # print("UID Length: {:d}".format(len(uid)))
        # print("UID Value: {}".format(binascii.hexlify(uid)))

        # Check in user
        user_id = str(binascii.hexlify(uid))
        lcdscreen.write_text(f"Scanned ID: {user_id}")

        # Send to backend
        integration.handle_check_in_or_out(user_id)

        # Clear console
        lcdscreen.clear_text()
        lcdscreen.write_text("Ready to scan...")

if __name__ == '__main__':
    setup()
    while True:
        loop()
