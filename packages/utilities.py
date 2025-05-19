# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which contains general functions which are used on multiple occasions
Version: 0.3.0 - 07-03-2024
"""

import os
import scipy.io
import math
import numpy as np

class activity_variables:
    def __init__(self, amplitude_times_baseline, min_event_freq, min_hpd_freq, min_spike_train_duration,
                 min_event_duration, min_ictal_hpd_duration, max_hvsw_duration, min_inter_event):
        self.amplitude_times_baseline = amplitude_times_baseline
        self.min_event_freq = min_event_freq
        self.min_hpd_freq = min_hpd_freq
        self.min_spike_train_duration =min_spike_train_duration
        self.min_event_duration = min_event_duration
        self.min_ictal_hpd_duration = min_ictal_hpd_duration
        self.max_hvsw_duration = max_hvsw_duration
        self.min_inter_event = min_inter_event
    
    
def extract_inter_ictal_spikes(input_data, spike_marker, events):
    inter_ictal_spikes = np.empty((0,3),int)
    j = 0
    for i in spike_marker:
        if(i[3] == 1):
            if(j==len(events)-1):
                if(i[0]>events[j][1]):
                    inter_ictal_spikes = np.append(inter_ictal_spikes, i[0:3].reshape(1,3), axis=0)
            else:
                if(i[0]<events[0][0]):
                    inter_ictal_spikes = np.append(inter_ictal_spikes, i[0:3].reshape(1,3), axis=0)
                elif(i[0]>events[j][1] and i[0]<events[j+1][0]):
                    inter_ictal_spikes = np.append(inter_ictal_spikes, i[0:3].reshape(1,3), axis=0)
                elif(i[0]>=events[j+1][0]):
                    j+=1
    detected_spike = create_spike_over_time(input_data, inter_ictal_spikes)
    return inter_ictal_spikes, detected_spike

def create_spike_per_time(input_data, spikes, per_time):
    spike_per_time = np.zeros((round(len(input_data)/per_time)+1,2), int)
    if(per_time==5000):
        for k in range(len(spike_per_time)):
            spike_per_time[k][0] = k*5
    else:
        for k in range(len(spike_per_time)):
            spike_per_time[k][0] = k+1
        
    for i in range(len(spikes)):
        spike_per_time[math.floor(spikes[i][0]/per_time)][1] += 1
    
    return spike_per_time

def create_event_per_time(input_data, events, per_time):
    event_per_time = np.zeros((round(len(input_data)/per_time)+1,4), int)
    for i in range(len(events)):
        if(per_time == 5000):
            if(events[i][0]%per_time > 2.5):
                start = math.floor(events[i][0]/per_time)
            else:
                start = math.floor(events[i][0]/per_time)+1
                
            if(events[i][1]%per_time > 2.5):
                end = math.floor(events[i][1]/per_time)+1
            else:
                end = math.floor(events[i][1]/per_time)
            
            for j in range(start, end):
                event_per_time[j][int(events[i][8])] = events[i][8]+1
        elif(per_time == 3600000):
            start =  math.floor(events[i][0]/per_time)
            end = math.floor(events[i][1]/per_time)
            if(start != end):
                if((end*per_time-events[i][0]) > (end*per_time-events[i][1])):
                    event_per_time[start][int(events[i][8])] += 1
                else:
                    event_per_time[end][int(events[i][8])] += 1
            else:
                event_per_time[start][int(events[i][8])] += 1
                
    return event_per_time

def create_spike_over_time(input_data, spikes):
    # Creating spike output array
    detected_spike = np.zeros((len(input_data),4), float)
    for i in range(len(spikes)):
        indice = int(spikes[i][0])
        detected_spike[indice][1] = 1
        detected_spike[indice][2] = spikes[i][1]
        detected_spike[indice][3] = spikes[i][2]
        
    for j in range(len(input_data)):
        detected_spike[j][0] = j
    
    return detected_spike

def create_event_over_time(input_data, events):
    event_over_time = np.zeros((len(input_data), 4), int)
    for i in range(len(input_data)):
        event_over_time[i][0] = i
    
    for j in range(len(events)):
        for k in range(int(events[j][0]),int(events[j][1])):
            if(events[j][8]==0):
                event_over_time[k][1] = 1
            elif(events[j][8]==1):
                event_over_time[k][2] = 2
            elif(events[j][8]==2):
                event_over_time[k][3] = 3
            
    return event_over_time
    
# Save the results of the spike and activity detection
def save_results(input_directory, input_file, input_eeg, spikes, spike_over_time, detected_activity, event_over_time, exclusion):
    # Variables for exporting the data
    output_directory = r'_results'
    extension_annotated = '_an_hr_'
    extension_activity = '_activity'
    extension_per_h = '_per_hour'
    extension_per_5s = '_per_5s'
    
    # Check if results folder already exists
    if not os.path.isdir(input_directory+input_file+output_directory):
        os.mkdir(input_directory+input_file+output_directory)
    else: 
        for dirpath, dirnames, filenames in os.walk(input_directory+input_file+output_directory):
            for name in filenames:
                os.remove(input_directory+input_file+output_directory+ r'/' + name)

    # Save spike detection
    if(detected_activity is not None):
        if(len(detected_activity)!=0):
            inter_ictal_spikes, inter_ictal_spike_over_time = extract_inter_ictal_spikes(input_eeg, spikes, detected_activity)
        else:
            inter_ictal_spikes = spikes
            inter_ictal_spike_over_time = spike_over_time
        spikes_per_hour = create_spike_per_time(input_eeg, inter_ictal_spikes, 3600000)
        spikes_per_5s = create_spike_per_time(input_eeg, inter_ictal_spikes, 5000)
        events_per_hour = create_event_per_time(input_eeg, detected_activity, 3600000)
        event_per_5s = create_event_per_time(input_eeg, detected_activity, 5000)
        per_hour = np.append(spikes_per_hour, events_per_hour, axis=1)
        per_5s = np.append(spikes_per_5s, event_per_5s, axis=1)
        hours = math.floor(len(input_eeg)/3600000)+1
        for i in range(0,hours):
            scipy.io.savemat(input_directory+input_file+output_directory+input_file+extension_annotated+str(i+1)+'.mat', {'time':inter_ictal_spike_over_time.T[0][i*3600000:(i+1)*3600000].astype(int),
                                                                                                                     'inter_ictal_spikes':inter_ictal_spike_over_time.T[1][i*3600000:(i+1)*3600000].astype(int),
                                                                                                                     'all_spikes':spike_over_time.T[1][i*3600000:(i+1)*3600000].astype(int),
                                                                                                                     'pos_amplitude':inter_ictal_spike_over_time.T[2][i*3600000:(i+1)*3600000],
                                                                                                                     'neg_amplitude':inter_ictal_spike_over_time.T[3][i*3600000:(i+1)*3600000],
                                                                                                                     'exclusion':exclusion[i*3600000:(i+1)*3600000],
                                                                                                                     'HVSW':event_over_time.T[1][i*3600000:(i+1)*3600000],
                                                                                                                     'sHPD':event_over_time.T[2][i*3600000:(i+1)*3600000],
                                                                                                                     'iHPD':event_over_time.T[3][i*3600000:(i+1)*3600000]})
        np.savetxt(input_directory+input_file+output_directory+input_file+extension_per_h+'.txt', per_hour, comments='', fmt='%4d, %10d, %4d, %4d, %4d, %4d', header='Hour, Num spikes, HVSW, sHPD, iHPD, spike wave')
        np.savetxt(input_directory+input_file+output_directory+input_file+extension_per_5s+'.txt', per_5s, comments='', fmt='%8d, %10d, %4d, %4d, %4d, %4d', header='5 Second, Num spikes, HVSW, sHPD, iHPD, spike wave')
        if(len(detected_activity)!=0):
            scipy.io.savemat(input_directory+input_file+output_directory+input_file+extension_activity+'.mat', {'start_sample':detected_activity.T[0], 'end_sample':detected_activity.T[1],
                                                                                                                'frequency':detected_activity.T[2], 'amount_of_spikes':detected_activity.T[3],
                                                                                                                'min_freq':detected_activity.T[4], 'max_freq':detected_activity.T[5],
                                                                                                                'ave_positive_peak':detected_activity.T[6], 'ave_negative_peak':detected_activity.T[7],
                                                                                                                'activity_type':detected_activity.T[8]})        
            np.savetxt(input_directory+input_file+output_directory+input_file+extension_activity+'.txt', detected_activity.T[0:9].T, comments='', fmt='%12d, %13d, %15f, %10d, %8d, %8d, %11f, %11f, %d',
                       header='start sample, finish sample, spike frequency, num spikes, min freq, max freq, ave pos amp, ave neg amp, 0=HVSW 1=sHPD 2=iHPD')
    else:
        spikes_per_hour = create_spike_per_time(input_eeg, spikes, 3600000)
        spikes_per_5s = create_spike_per_time(input_eeg, spikes, 5000)
        hours = math.floor(len(input_eeg)/3600000)+1
        for i in range(0,hours):
            scipy.io.savemat(input_directory+input_file+output_directory+input_file+extension_annotated+str(i+1)+'.mat', {'time':spike_over_time.T[0][i*3600000:(i+1)*3600000].astype(int),
                                                                                                                      'all_spikes':spike_over_time.T[1][i*3600000:(i+1)*3600000].astype(int),
                                                                                                                      'pos_amplitude':spike_over_time.T[2][i*3600000:(i+1)*3600000],
                                                                                                                      'neg_amplitude':spike_over_time.T[3][i*3600000:(i+1)*3600000],
                                                                                                                      'exclusion':exclusion[i*3600000:(i+1)*3600000]})
        np.savetxt(input_directory+input_file+output_directory+input_file+extension_per_h+'.txt', spikes_per_hour, comments='', fmt='%4d, %10d', header='Hour, Num spikes')
        np.savetxt(input_directory+input_file+output_directory+input_file+extension_per_5s+'.txt', spikes_per_5s, comments='', fmt='%8d, %10d', header='5 Second, Num spikes')