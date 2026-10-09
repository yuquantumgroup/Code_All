import TimeTagger
from TimeTagger import TimeTaggerBase, Coincidence, Coincidences, CoincidenceTimestamp, FileReader, TimeTagStream, Correlation, Counter, DelayedChannel

s_to_ps = lambda s: s*1e12
ps_to_s = lambda p: p*1e-12

def set_time_tagger():
    acq_time = 1 #s
    bw = 0.000001 #in s

    tagger = TimeTagger.createTimeTagger()

    ### Define the hardware settings here, such as trigger level or dead time. 
    for ch in [1, 2]:
        tagger.setTriggerLevel(-ch, -0.3)
    tagger.setInputDelay(-1, 0) #ps
    tagger.setInputDelay(-2, 0)

    ### active channels for this measurement
    ch =[1,2]
    tot_ch = ch#+list(cc_ch.getChannels())
    return tagger, tot_ch, acq_time, bw

def get_photon_counts():
    counter = TimeTagger.Counter(tagger=tagger, channels=tot_ch, binwidth=s_to_ps(bw), n_values=100)
    counter.startFor(int(s_to_ps(acq_time)))
    counter.waitUntilFinished()
    obj = counter.getDataObject()
    data = obj.getData()

    ch1_counts = sum(data[0])
    ch2_counts = sum(data[1])
    return ch1_counts, ch2_counts


tagger, tot_ch, acq_time, bw = set_time_tagger()
ch1_counts, ch2_counts = get_photon_counts()
print("Channel 1 Counts:", ch1_counts)
print("Channel 2 Counts:", ch2_counts)