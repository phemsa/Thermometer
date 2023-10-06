#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 22:28:53 2021

@author: phemsa
"""
from time import time
from struct import unpack

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.colors as mcolors
from scipy.signal import argrelextrema as arex

sensorNames = {'<MAC_address>': '<name>',
               '12:34:56:78:90:AB': 'Raum 2'}


class Readings():

    def __init__(self, infile):
        start = time()
        self.read(infile)
        ms = (time() - start)*1000.; start = time()
        print(f"Read time: {ms:.2f}ms")
        self.process()
        ms = (time() - start)*1000.; start = time()
        print(f"Process time: {ms:.2f}ms")

    def read(self, infile):

        readings = []

        with open(infile, 'r') as f:
            for line in f:

                temp, hum, i = 0, 0, 0

                for val in line.split("value: ")[1:]:
                    if len(val) > 7:
                        t, h = unpack('<hB', bytearray.fromhex(val[:8]))
                        temp, hum, i = temp + t/100., hum + h, i+1

                if i:
                    line = line.strip('\x00')
                    timestamp = int(line[:10])+3600
                    readings.append((line[11:28], timestamp, temp/i, hum/i))

        self.df = pd.DataFrame(readings, columns=['sensor','time','temp','hum'])

    def process(self):

        self.df["time"] = pd.to_datetime(self.df["time"], unit='s')
        self.df['sensor'].replace(sensorNames, inplace=True)
        self.temp = self.df.pivot_table(index="time", columns="sensor", values="temp")
        self.hum = self.df.pivot_table(index="time", columns="sensor", values="hum")


    def formatIndex(self, df, ax=None, period='D'):
        if ax is None: ax = plt.gca()
        ax.grid(alpha=0.2)
        ticks = df.resample(period).sum().index
        ax.set_xticks(ticks)
        fmts = ' '.join(['%d' if 'D' in period else '', '%b'])
        ax.set_xticklabels(ticks.strftime(fmts), rotation=90)


    def plotTemperatures(self, interval='1h'):
        df = self.temp.resample(interval).mean()
        ax = df.plot()
        self.formatIndex(df, ax, 'MS')


    def plotLastMonth(self, interval='1h'):
        df = self.temp.resample(interval).mean()
        ax = df.plot()
        self.formatIndex(df, ax, 'D')

        now = pd.Timestamp('now')
        ax.set_xlim([now - pd.DateOffset(months=1), now])


    def plotInterpolated(self, interval='1h'):
        df = self.temp.rolling(interval, center=True).mean()
        ax = df.plot()


    def hist(self, interval='1h'):
        t = self.temp.resample(interval).mean()

        for sensor in t:
            df = t[sensor]

            ndays = (df.index.max() - df.index.min()).days
            times = md.date2num(df.index.values)

            fig, ax = plt.subplots()
            fig.suptitle(sensor)
            ax.set_facecolor('k')

            ax.hist2d(md.date2num(df.index), df,
                      range=np.array([[times.min(), times.max()], [df.min(), df.max()]]),
                      bins=[int(ndays), 100],
                      cmap='magma',
                      norm=mcolors.LogNorm())

            self.formatIndex(df, ax, 'MS')
            ax.set_yticks(np.arange(-10, 50, 5))
            ax.set_yticks(np.arange(-10, 50), minor=True)
            ax.axhline(0, c='w', linestyle='--')


    def plotHumidity(self, interval='1h'):
        df = self.hum.resample(interval).mean()
        axs = df.plot(subplots=True, layout=(4,3), sharey=True)

        for ax in axs.flat:
            ax.axhline(0, c='k', linestyle='--')
            ax.grid(which='both', alpha=0.2)


    def plotDailyCourse(self):
        perHour = self.temp.groupby(self.temp.index.hour).mean()
        perHour.plot(subplots=True, layout=(4,3), grid=True)


    def plotPerSensor(self, interval='1h'):
        df = self.temp.resample(interval).mean()
        axs = df.plot(subplots=True, layout=(4,3), sharey=True)

        for ax in axs.flat:
            ax.axhline(0, c='k', linestyle='--')
            ax.grid(which='both', alpha=0.2)


if __name__ == "__main__":

    readings = Readings("/home/pi/Temperaturen.txt")
    readings.plotTemperatures('1h')
    readings.plotHumidity('1h')
    readings.plotPerSensor('1h')
    readings.hist()





