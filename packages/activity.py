# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File containing the functions necessary to run activity detection
Version: 0.3.0 - 07-03-2024
"""

import numpy as np
import pandas as pd
import math
from packages.utilities import create_event_over_time
from packages.event_class import event

def combine_half_events(current_event, half_event, spike_marker, spike_min_amp, input_variables, i):
    combine = False
    distance = current_event.start_sample-half_event.stop_sample
    duration = current_event.stop_sample-half_event.start_sample
    if(duration>0):
        cur_freq = ((current_event.num_spikes+half_event.num_spikes)*1000)/(duration)
        if(distance<=input_variables.min_inter_event and duration>=input_variables.min_event_duration and cur_freq>=input_variables.min_event_freq):
            combine = True
            current_event.start_sample = half_event.start_sample
            current_event.frequency = cur_freq
            current_event.ave_neg_peak = current_event.ave_neg_peak*current_event.num_spikes + half_event.ave_neg_peak*half_event.num_spikes
            current_event.ave_pos_peak = current_event.ave_pos_peak*current_event.num_spikes + half_event.ave_pos_peak*half_event.num_spikes
            current_event.num_spikes += half_event.num_spikes
            current_event.ave_neg_peak = current_event.ave_neg_peak/current_event.num_spikes
            current_event.ave_pos_peak = current_event.ave_pos_peak/current_event.num_spikes
            
            j = half_event.start_sample_i
            start_sec = half_event.start_sec
            end_sec = math.floor(current_event.stop_sample/1000)
            spike_per_sec = np.zeros(end_sec-start_sec+1, int)        
            while(spike_marker[j][0] <= current_event.stop_sample):
                if(spike_marker[j][1]>spike_min_amp or (-1*spike_marker[j][2])>spike_min_amp):
                    cur_sec = math.floor(spike_marker[j][0]/1000)
                    spike_per_sec[cur_sec-start_sec] += 1
                j+=1
            current_event.min_freq = min(spike_per_sec)
            current_event.max_freq = max(spike_per_sec)
            current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
            current_event.classification = 0
    
    return current_event, combine

def combine_two_events(last_event, current_event, spike_marker, spike_min_amp):
    last_event.stop_sample = current_event.stop_sample
    last_event.ave_pos_peak = current_event.ave_pos_peak*current_event.num_spikes + last_event.ave_pos_peak*last_event.num_spikes
    last_event.ave_neg_peak = current_event.ave_neg_peak*current_event.num_spikes + last_event.ave_neg_peak*last_event.num_spikes
    last_event.num_spikes = 0
    for i in range(int(last_event.start_sample_i), int(current_event.stop_sample_i)+1):
        if(spike_marker[i][1]>spike_min_amp or (-1*spike_marker[i][2])>spike_min_amp):
            last_event.num_spikes += 1
    last_event.frequency = (last_event.num_spikes*1000)/(last_event.stop_sample-last_event.start_sample)
    last_event.min_freq = 0
    last_event.ave_pos_peak = last_event.ave_pos_peak/last_event.num_spikes
    last_event.ave_neg_peak = last_event.ave_neg_peak/last_event.num_spikes
    if(current_event.max_freq>last_event.max_freq):
        last_event.max_freq = current_event.max_freq  
    if(current_event.classification==2 or last_event.classification == 2):
        last_event.classification = 2
    elif(current_event.classification==1 or last_event.classification == 1):
        last_event.classification = 1
    else:
        last_event.classification=0
    if(current_event.max_five_second_spike>last_event.max_five_second_spike):
        last_event.max_five_second_spike = current_event.max_five_second_spike
    return last_event
    
def calculate_baseline(eeg_data_base, spike_marker, base_line_level):
    baseline_found = False
    if((spike_marker[0][0] - 100) > 30000):
        corrected_signal = eeg_data_base[0:29999]
        baseline_found = True
    
    base_length = [30000, 20000, 15000, 10000, 5000]
    j = 0
    while not baseline_found:
        for i in range(1,len(spike_marker)):
            if((spike_marker[i][0] - 100) - (spike_marker[i-1][0] + 100) > base_length[j]):
                corrected_signal = eeg_data_base[int(spike_marker[i-1][0])+1000:int(spike_marker[i-1][0])+(base_length[j]-2000)]
                baseline_found = True
                break
        if(j<4):
            j+=1
        else:
            break
    spike_amp = base_line_level*np.percentile(abs(corrected_signal), 97)    
    return spike_amp
    
def detect_activity(eeg_data_base, spike_marker, input_variables):
    spike_min_amp = calculate_baseline(eeg_data_base, spike_marker, input_variables.amplitude_times_baseline)
    spike_marker = np.append(spike_marker, np.zeros(len(spike_marker)).reshape(len(spike_marker),1), axis=1)
    
    epileptiform_event = []
    events = 0
    last_spike = 0
    last_spike_i = 0
    first_loop = 0

    while 1:
        if(spike_marker[first_loop][1]>spike_min_amp or (-1*spike_marker[first_loop][2])>spike_min_amp):
            spike_marker[first_loop][3] = 1
            last_spike = spike_marker[first_loop][0]
            last_spike_i = first_loop
            break
        first_loop += 1
        
    for j in range(first_loop+1, len(spike_marker)):
        events = len(epileptiform_event)
        if(events!=0 and spike_marker[j][0] <= epileptiform_event[events-1].stop_sample):
            continue
        for i in range(j, len(spike_marker)):
            if(spike_marker[i][1]>spike_min_amp or (-1*spike_marker[i][2])>spike_min_amp):
                spike_marker[i][3] = 1
                try:
                    current_event
                except NameError:
                    current_event = event(spike_marker[i], i)
                else:
                    if(spike_marker[i][0] - last_spike < input_variables.min_inter_event):
                        if(not current_event.check_new_frequency(spike_marker[i], input_variables.min_event_freq)):
                            current_event.define_end_event(last_spike, last_spike_i)
                            if((last_spike-current_event.start_sample > input_variables.min_event_duration) and current_event.num_spikes!=0):
                                if(events !=0 and current_event.start_sample - epileptiform_event[events-1].stop_sample < input_variables.min_inter_event):
                                    current_event.classify_event(input_variables)
                                    epileptiform_event[events-1] = combine_two_events(epileptiform_event[events-1], current_event, spike_marker, spike_min_amp)
                                else:
                                    current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
                                    current_event.classify_event(input_variables)
                                    while(events != 0 and current_event.start_sample <= epileptiform_event[events-1].start_sample):
                                        epileptiform_event.pop(events-1)
                                        events -= 1
                                        
                                    if(events !=0 and current_event.start_sample - epileptiform_event[events-1].stop_sample < input_variables.min_inter_event):
                                        epileptiform_event[events-1] = combine_two_events(epileptiform_event[events-1], current_event, spike_marker, spike_min_amp)
                                    else:
                                        epileptiform_event.append(current_event)
                                        events += 1
                            elif((last_spike-current_event.start_sample > input_variables.min_spike_train_duration) and current_event.num_spikes!=0):
                                current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
                                if(current_event.stop_sample-current_event.start_sample > input_variables.min_event_duration):
                                    current_event.classify_event(input_variables)
                                else:
                                    current_event.classification = 3
                                epileptiform_event.append(current_event)
                                events += 1
                            else:
                                try:
                                    current_event, combine = combine_half_events(current_event, half_event, spike_marker, spike_min_amp, input_variables, i)
                                    if(combine):
                                        epileptiform_event.append(current_event)
                                        events += 1
                                    else:
                                        half_event = current_event
                                except NameError:
                                    half_event = current_event
                            del current_event
                            last_spike = spike_marker[i][0]
                            last_spike_i = i
                            break
                    else:
                        current_event.define_end_event(last_spike, last_spike_i)
                        current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
                        current_event.classify_event(input_variables)
                            
                        if((last_spike-current_event.start_sample > input_variables.min_event_duration) and current_event.num_spikes!=0):
                            if(events !=0 and current_event.start_sample - epileptiform_event[events-1].stop_sample < input_variables.min_inter_event):
                                epileptiform_event[events-1] = combine_two_events(epileptiform_event[events-1], current_event, spike_marker, spike_min_amp)
                                
                                while(events != 0 and current_event.start_sample <= epileptiform_event[events-1].start_sample):
                                    epileptiform_event.pop(events-1)
                                    events -= 1
                            else:
                                while(events != 0 and current_event.start_sample <= epileptiform_event[events-1].start_sample):
                                    epileptiform_event.pop(events-1)
                                    events -= 1
                                epileptiform_event.append(current_event)
                                events += 1
                        elif((last_spike-current_event.start_sample > input_variables.min_spike_train_duration) and current_event.num_spikes!=0):
                            current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
                            current_event.classification = 3
                            epileptiform_event.append(current_event)
                            events += 1
                        else:
                            try:
                                current_event, combine = combine_half_events(current_event, half_event, spike_marker, spike_min_amp, input_variables, i)
                                if(combine):
                                    epileptiform_event.append(current_event)
                                    events += 1
                            except NameError:
                                pass
    
                        del current_event
                        last_spike = spike_marker[i][0]
                        last_spike_i = i
                        break
                last_spike = spike_marker[i][0]
                last_spike_i = i
                    
                if(spike_marker[i][0]-spike_marker[i-1][0] >= 30000):
                    spike_min_amp = 0.2*(2*np.percentile(abs(eeg_data_base[int(spike_marker[i][0])-25000:int(spike_marker[i][0])-5000]), 97)) + 0.8*spike_min_amp

    
    try:
        if(current_event.num_spikes > 1):
            current_event.define_end_event(last_spike, last_spike_i)
            current_event.check_preliminary_spikes(spike_marker, spike_min_amp, input_variables.min_event_freq)
            current_event.classify_event(input_variables)
            if((last_spike-current_event.start_sample > input_variables.min_event_duration) and (current_event.frequency >= 2)):
                if(events !=0 and current_event.start_sample - epileptiform_event[events-1].stop_sample < input_variables.min_inter_event):
                    epileptiform_event[events-1] = combine_two_events(epileptiform_event[events-1], current_event, spike_marker, spike_min_amp)
                    
                    while(events != 0 and current_event.start_sample <= epileptiform_event[events-1].start_sample):
                        epileptiform_event.pop(events-1)
                        events -= 1
                else:
                    while(events != 0 and current_event.start_sample <= epileptiform_event[events-1].start_sample):
                        epileptiform_event.pop(events-1)
                        events -= 1
                    epileptiform_event.append(current_event)
                    events += 1
    except NameError:
        pass

    if(len(epileptiform_event)!=0):
        # Start_time, End_time, Frequency, amount_spikes, min_freq, max_freq, ave_pos_peak, ave_neg_peak, 0=HVSWs 1=HPD 2=grey_zone
        epileptiform_event = pd.DataFrame([vars(t) for t in epileptiform_event])
        epileptiform_event = epileptiform_event[['start_sample', 'stop_sample', 'frequency', 'num_spikes', 'min_freq', 'max_freq', 'ave_pos_peak', 'ave_neg_peak', 'classification']]
        epileptiform_event = epileptiform_event.to_numpy()
        
    event_over_time = create_event_over_time(eeg_data_base, epileptiform_event)

    return epileptiform_event, event_over_time, spike_marker