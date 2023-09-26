import binascii

from pn532pi import Pn532, pn532, Pn532I2c

import os
import time
import integration

# Set up I2C
PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)


def setup():
    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if (not versiondata):
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    #  Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    #  configure board to read RFID tags
    nfc.SAMConfig()

    os.system("clear")

    # print("Waiting for an ISO14443A Card ...")
    print("Ready to scan...")


def loop():
    #  Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    #  'uid' will be populated with the UID, and uidLength will indicate
    #  if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if (success):
        #  Display some basic information about the card
        print("Found an ISO14443A card")
        # print("UID Length: {:d}".format(len(uid)))
        # print("UID Value: {}".format(binascii.hexlify(uid)))

        # Check in user
        user_id = str(binascii.hexlify(uid))
        print(f"Scanned ID: {user_id}")

        # Send to backend
        integration.handle_check_in_or_out(user_id)

        # Sleep before clearing console
        time.sleep(10)
        os.system("clear")
        

    return False

if __name__ == '__main__':
    setup()
    found = loop()
    while not found:
        found = loop()
