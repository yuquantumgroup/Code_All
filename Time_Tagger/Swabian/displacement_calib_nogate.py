# -*- coding: utf-8 -*-

import os
import numpy as np
import TimeTagger
from TimeTagger import TimeTaggerBase, Coincidence, Coincidences, CoincidenceTimestamp, FileReader, TimeTagStream, Correlation, Counter, DelayedChannel
import time
import csv 

acq_time = 1 #s
bw = 0.000001 #in s

#from qubib.devices.swabian_instruments.TimeTaggerSwabian import TimeTaggerSwabian

s_to_ps = lambda s: s*1e12
ps_to_s = lambda p: p*1e-12

#connect to network time tagger
#tagger = TimeTagger.createTimeTaggerNetwork('10.42.0.134')
tagger = TimeTagger.createTimeTagger()
#tagger.setHardwareBufferSize(536870912) # was 67108864(536870912)

#frequency_channel = 1 
#PPS_channel = 2 
# Define the hardware settings here, such as trigger level or dead time. 
for ch in [1, 2]:
    tagger.setTriggerLevel(-ch, -0.3)
tagger.setInputDelay(-1, 0) #ps
tagger.setInputDelay(-2, 0)
# Enable the ReferenceClock 
#tagger.setReferenceClock(clock_channel=frequency_channel, clock_frequency=10e6, time_constant = 1e-3, synchronization_channel=2, wait_until_locked=True)

#cc_grp = [[3,7],[3,8],[3,9],[3,10],[4,7],[4,8],[4,9],[4,10]]
#cc_ch = Coincidences(tagger, cc_grp, coincidenceWindow=1000)

#tot_ch = [*channels, *cc_ch.getChannels()]


#tagger.setHardwareBufferSize(512)

#active channels for this measurement
ch =[1,2]
#cc_grp = [[ch3d,ch7d],[ch3d,ch8d],[ch3d,ch9d],[ch3d,ch10d],[4,ch7d],[4,ch8d],[4,ch9d],[4,ch10d]]
#cc_ch = Coincidences(tagger, cc_grp, coincidenceWindow=1500)
tot_ch = ch#+list(cc_ch.getChannels())

counter0 = TimeTagger.Counter(tagger=tagger, channels=tot_ch, binwidth=s_to_ps(0.1), n_values=10_000)
counter0.startFor(int(s_to_ps(3)))
counter0.waitUntilFinished()
obj = counter0.getDataObject()
data_norm = obj.getDataNormalized()
print("Data Normalized", data_norm)

time.sleep(1)

counter = TimeTagger.Counter(tagger=tagger, channels=tot_ch, binwidth=s_to_ps(bw), n_values=10_000_000)
counter.startFor(int(s_to_ps(acq_time)))
counter.waitUntilFinished()
obj = counter.getDataObject()
data = obj.getData()
print(data.shape)
print(data)

#calculating alpha
alpha_ch2 = np.mean(data[1])
alpha_ch1 = np.mean(data[0])

print("Ch1 Alpha", alpha_ch1)
print("Ch2 Alpha", alpha_ch2)
print("Sum of Alphas:")
print(alpha_ch1+alpha_ch2)


#fname = fr'C:\Users\SERF321\Documents\YuGroupCode\Time_Tagger\Swabian\test_092426.csv'
#with open(fname, 'w') as file:
    #writer = csv.writer(file)
    #writer.writerow(["Time(s)", "CH1", "CH2"])
#time.sleep(2)
#n_cyl = 10*3600*10
#for  _ in range(n_cyl):

#with open(fname, mode="a", newline="") as file:
    #writer = csv.writer(file)

#%%

TimeTagger.freeTimeTagger(tagger)
# %%
