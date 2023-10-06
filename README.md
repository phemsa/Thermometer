# Thermometer
Reads Xiaomi/Mijia bluetooth thermo sensors from a raspberri pi and diplays on a Waveshare e-ink display

# Components
- A Raspberri Pi (I am using a Pi Zero WH) with bluetooth enabled and gatttool (should on there out of the box)
- Xiaomi Mijia Bluetooth 2 Wireless Thermometer (LYWSD03MMC)
- If you want to display, a Waveshare E-ink Display (I am using a Waveshare 7.5inch HD e-Paper HAT)
- The Waveshare python libraries for your respective display e.g. from https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT
- The 7.5 inch e-ink display fits an IKEA Ribba 13 x 18 cm frame with surprisingly little dead space

# Files
thermometer_harvester.sh
Goes through a list of bluetooth MAC addresses of Xiaomi Mijia bluetooth thermo sensors and queries them for their temperature and humidity readings.
All readings including their bluetooth blurb are stored in a file called "Thermometer.csv".
I usually run this every 15 min as a cron job

epaper_thermometer.py
Plots temperatures read by thermometer_harvester.sh on a Waveshare e-ink display. This file is based on the Waveshare Python template of the 7.5 inch display in HAT version

temperature_plotter.py
Plots temperatures in python in various formats and tricks
