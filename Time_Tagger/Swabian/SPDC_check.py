# -*- coding: utf-8 -*-
"""
Modified based on Doroteas' code on Mon Oct 1 2026

@author: Landon
"""
from math import sqrt
import os
import numpy as np
import TimeTagger
from TimeTagger import TimeTaggerBase, Coincidence, Coincidences, CoincidenceTimestamp, FileReader, TimeTagStream, Correlation, Counter, DelayedChannel
import time
import csv

acq_time = 5 #s
bw = 0.1 #in s

s_to_ps = lambda s: s*1e12
ps_to_s = lambda p: p*1e-12

tagger = TimeTagger.createTimeTagger()

# Define the hardware settings here, such as trigger level or dead time. 
for ch in [1, 2,3]:
    tagger.setTriggerLevel(-ch, -0.3)
tagger.setInputDelay(-1, 0) #ps
tagger.setInputDelay(-2, 0)
tagger.setInputDelay(-3, 0)

#active channels for this measurement
ch =[1,2,3]
cc_grp = [[1,3],[2,3]]
cc_ch = Coincidences(tagger, cc_grp, coincidenceWindow=1500)
tot_ch = ch+list(cc_ch.getChannels())

counter = TimeTagger.Counter(tagger=tagger, channels=tot_ch, binwidth=s_to_ps(bw), n_values=100)
counter.startFor(int(s_to_ps(acq_time)))
counter.waitUntilFinished()
obj = counter.getDataObject()
data = obj.getData()

total_cc = sum(data[3:4])
total_ch1_counts = sum(data[0])
total_ch2_counts = sum(data[1])
total_ch3_counts = sum(data[2])
cc_coeff = total_cc/np.sqrt(((total_ch1_counts+total_ch2_counts)*total_ch3_counts))

print("\nCh1 Counts", total_ch1_counts)
print("\nCh2 Counts", total_ch2_counts)
print("\nCh3 Counts", total_ch3_counts)
print("\nCC1-3 Counts", data[3])
print("\nCC2-3 Counts", data[4])
print("\nTotal CC", total_cc)
print("\nCC Coefficient", cc_coeff)

#close time tagger
TimeTagger.freeTimeTagger(tagger)