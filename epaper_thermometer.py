#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Based on Waveshare e-ink display python template

import sys
import os
import logging
import time
import traceback
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

from struct import unpack
from PIL import Image, ImageDraw, ImageFont



### Script wide constants

fontdir = '/home/pi/fonts'
libdir = '/home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib'

TEMPERATUREN_CSV = '/home/pi/Temperaturen.csv'
TEMPERATUREN_TXT = '/home/pi/Temperaturen.txt'
NEUESTE = '/home/pi/neueste.txt'

# Change to your waveshare display
sys.path.append(libdir)
from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.INFO)

# Preset Image/Text sizes. Display resolution: 800x480 px
S = ImageFont.truetype(os.path.join(fontdir, 'HelveticaNeueLTStd-Roman.otf'), 18)
M = ImageFont.truetype(os.path.join(fontdir, 'HelveticaNeueLTStd-Roman.otf'), 32)
L = ImageFont.truetype(os.path.join(fontdir, 'HelveticaNeueLTStd-Roman.otf'), 38)
XL = ImageFont.truetype(os.path.join(fontdir, 'HelveticaNeueLTStd-Blk.otf'), 42)

FRAME = 30 #pixels

sensorNames = {'<MAC_address>': '<name>',
               '12:34:56:78:90:AB': 'Raum 2'}

### Data handling functions

def processInputFiles():
    """ Reads the output file of the bash script and filters out broken records.
    Writes into harcoded txt files for all values (Temperaturen.txt) and
    last 100 records for the e-ink display (neueste.txt) """

    out = []

    with open(TEMPERATUREN_CSV,'r') as f:
        for line in f:
            line = line.replace('Characteristic value was written successfully ', '')
            line = line.replace('Notification handle = 0x0036 ', '')
            if len(line.split('value: ')) != 1:
                out.append(line)

    with open(TEMPERATUREN_TXT,'w') as file:
        file.write(''.join(out))

    with open(NEUESTE,'w') as file:
        file.write(''.join(out[-100::]))


def readTemperatures(infile):
    """ Reads a tex file written by processInputFiles into a Pandas data frame. """

    readings = []

    with open(infile, 'r') as f:
        for line in f:

            temp, hum, i = 0, 0, 0

            for val in line.split("value: ")[1:]:
                if len(val) > 7:
		    # If the sensor provided a value, unpack into floats and add up
                    t, h = unpack('<hB', bytearray.fromhex(val[:8]))
                    temp, hum, i = temp + t/100., hum + h, i+1

            if i:
                line = line.strip('\x00')
                # 7200: Adjust for summer time (remove if your raspi has correct time)
                timestamp = int(line[:10]) + 7200
                # divide by the number of readings to take the mean
                readings.append((line[11:28], timestamp, temp/i, hum/i))

    df = pd.DataFrame(readings, columns=['sensor','time','temp','hum'])
    df["time"] = pd.to_datetime(df["time"], unit='s')
    df['sensor'] = df['sensor'].replace(sensorNames, regex=True)

    # Invalidate (set to NaN) all values that are older than 1h
    grouped = df.groupby(['sensor'])
    newest = df.loc[grouped["time"].idxmax()]
    tooOld = (pd.Timestamp.now() - newest["time"]) > pd.Timedelta('60 minute')
    newest["temp"][tooOld] = np.nan

    return newest

### Drawing functions

def addSensor(offset, df, draw):
    name = df["sensor"]
    temp = '{0:0>4.1f}°C'.format(df["temp"])
    draw.text((FRAME+2, offset+2), name, font=L,  fill=0, anchor="ls")
    draw.text((300, offset), temp, font=XL, fill=0, anchor="ls")
    return offset + 60

### Main Loop

try:
    logging.info("Proceesing input data")
    processInputFiles()
    logging.info("Reading Temperature data")
    readings = readTemperatures(NEUESTE)
    logging.info("Initializing Display")
    epd = epd7in5_V2.EPD()
    epd.init()

    logging.info("Creating Clear Image")
    im = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(im)
    offset = FRAME + 50 #pixel

    logging.info("Drawing Headline")
    now = time.strftime("%H:%M")
    draw.text((FRAME, offset), 'Aktuelle Temperaturen {}'.format(now), font=M, fill=0)
    draw.line((FRAME+2, offset+36, 450, offset+36), fill=0)

    logging.info("Drawing Sensor data")
    offset += 70
    for _, row in readings.iterrows():
        offset = addSensor(offset, row, draw)

    logging.info("Calling display routine")
    epd.display(epd.getbuffer(im))

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
