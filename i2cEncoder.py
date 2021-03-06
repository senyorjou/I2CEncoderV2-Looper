# I2CEncoderV2
# Library: https://github.com/Fattoresaimon/I2CEncoderV2/blob/master/Raspberry%20Library/smbus2/i2cEncoderLibV2.py
# Date: 2019/05/17
# Author: https://github.com/retroriff

import random

import smbus2
from gpiozero import Button
import i2cEncoderLibV2


def init_encoder(min_val, max_val):
    bus = smbus2.SMBus(1)
    encoder = i2cEncoderLibV2.i2cEncoderLibV2(bus, 0x21)

    encconfig = (i2cEncoderLibV2.INT_DATA |
                 i2cEncoderLibV2.WRAP_DISABLE |
                 i2cEncoderLibV2.DIRE_RIGHT |
                 i2cEncoderLibV2.IPUP_ENABLE |
                 i2cEncoderLibV2.RMOD_X1 |
                 i2cEncoderLibV2.RGB_ENCODER)
    encoder.begin(encconfig)
    encoder.writeCounter(max_val/2)
    encoder.writeMax(max_val)
    encoder.writeMin(min_val)
    encoder.writeStep(1)
    encoder.writeInterruptConfig(0xff)

    return encoder


int_pin = Button(4)

min_val, max_val = 0, 10.0
exp_growth = 3

encoder = init_encoder(min_val, max_val)

try:
    while True:
        if int_pin.is_pressed:
            encoder.updateStatus()
            change_color = False
        # Encoder turn right
        if encoder.readStatus(i2cEncoderLibV2.RINC):
            change_color = True

        # Encoder turn left
        if encoder.readStatus(i2cEncoderLibV2.RDEC):
            change_color = True

        # Encoder pushed
        if encoder.readStatus(i2cEncoderLibV2.PUSHP):
            print("Click")
            encoder.writeCounter(random.randint(min_val, max_val))
            change_color = True

        if change_color:
            counter = encoder.readCounter32()
            # Default values
            c = 0
            color = '0x00'
            printColor = "Off"

            # Set color Red
            if counter > max_val / 2:
                color_step = (max_val - counter + 1) ** exp_growth
                c = int(255 / color_step)
                color = '0x{:02x}{:02x}{:02x}'.format(c, 0, 0)
                printColor = "Red"

            # Set color Blue
            if counter < max_val / 2:
                colorStep = counter + 1 ** exp_growth
                c = int(255 / colorStep)
                color = '0x{:02x}{:02x}{:02x}'.format(0, 0, c)
                printColor = "Blue"

            if (not encoder.readStatus(i2cEncoderLibV2.RMAX) and
                    not encoder.readStatus(i2cEncoderLibV2.RMIN)):
                encoder.writeRGBCode(int(color, 0))
                print('Counter: {} {}: {}'.format(counter, printColor, c))

except KeyboardInterrupt:
    encoder.writeInterruptConfig(0xff)
    print("\nExit.")
