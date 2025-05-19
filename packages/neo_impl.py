# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File containing the functions necessary to run spike detection
Version: 0.3.0 - 07-03-2024
"""

import numpy as np
import scipy.io
import mat73
from packages.utilities import create_spike_over_time

# Function to mark spikes using a timeseries and a threshold input
def get_spike_time(data, original_data, spike_window, thresh):
    exclusion = np.zeros(len(original_data), int)
    # Create array where threshold is crossed
    if(thresh >0):
        pos = np.where(data > thresh)[0]
        pos = pos[pos > spike_window]
        last_spike_samp = 0
    else:
        pos = np.where(data < thresh)[0]
        pos = pos[pos > spike_window]
        last_spike_samp = 0

    # Extract spikes
    spike_mark = np.empty((0,3), float)
    # wave_form = np.empty((0,2*spike_window), int)
    tmp_samp = np.zeros(3, float)
    for i in pos:
        if i < data.shape[0] - (2*spike_window+1):
            if i > (last_spike_samp + 2*spike_window):
                # Save temporary spike location and waveform
                tmp_waveform = original_data[i-spike_window+10:i+spike_window+10]
                tmp_samp[0] = i
                tmp_samp[1] = max(tmp_waveform)
                tmp_samp[2] = min(tmp_waveform)

                # Append data to existing array
                if(tmp_samp[1]<=6 and tmp_samp[2]>=-6):
                    spike_mark = np.append(spike_mark, tmp_samp.reshape(1, 3), axis=0)
                    last_spike_samp = tmp_samp[0]
                    # wave_form = np.append(wave_form, tmp_waveform.reshape(1, spike_window*2), axis=0)
                else:
                    exclusion[i] = 1

    return spike_mark, exclusion

# Function which executes the NEO implementation with automatic thresholding
def NEO(eeg_data):
    #Loading the necessary arrays for the IIR filter
    length = len(eeg_data)
    eeg_iir = np.zeros(length)
    neo = np.zeros(length)
    neo_iir = np.zeros(length)
    base_val = np.zeros(length)
    
    #IIR filters
    alpha = 1/4
    beta = 3/32
    gamma = 1/300
    
    for i in range(1, length-1):
        base_val[i] = gamma*eeg_data[i-1] + (1-gamma)*base_val[i-1]

    eeg_data_base = eeg_data - base_val
    
    eeg_iir[1] = alpha*eeg_data_base[0] + (1-alpha)*eeg_iir[0]
    for i in range(1, length-1):
        eeg_iir[i+1] = alpha*eeg_data_base[i] + (1-alpha)*eeg_iir[i]
        neo[i] = (eeg_iir[i]*eeg_iir[i]) - (eeg_iir[i-1]*eeg_iir[i+1])
        neo_iir[i] = beta*neo[i-1] + (1-beta)*neo_iir[i-1]
    
    return eeg_data_base, eeg_iir, neo_iir

def threshold_calc_detect(eeg_data, eeg_data_base, eeg_iir, neo_iir, threshold_constant):
    length = len(eeg_data)
    zero_cross = np.where(np.diff(eeg_data[0:length] > 0) != 0)[0] + 1
    zero_cross = (len(zero_cross) / (2 * length)) * (2 * np.pi)
    zero_cross = zero_cross**2
    std = (np.median(abs(eeg_iir[0:length]))/0.6745)**2
    thresh = zero_cross*std*threshold_constant

    spike_marker, exclusion = get_spike_time(neo_iir, eeg_data_base, spike_window=50, thresh=thresh)
    spike_over_time = create_spike_over_time(eeg_data, spike_marker)
    
    return spike_marker, spike_over_time, exclusion

# Function which does one run of spike detection and creates the output for given input
def run_spike_detection(input_directory, input_file, threshold_constant):
    try:
        input_data = scipy.io.loadmat(input_directory+input_file+'.mat')
        input_data = input_data['data'].T[0].T
    except:
        input_data = mat73.loadmat(input_directory+input_file+'.mat')
        input_data = input_data['data']
    
    # Spike detection
    eeg_data_base, eeg_iir, neo_iir = NEO(input_data)
    spikes, spike_over_time, exclusion = threshold_calc_detect(input_data, eeg_data_base, eeg_iir, neo_iir, threshold_constant)

    return spikes, eeg_data_base, spike_over_time, input_data, exclusion, eeg_iir, neo_iir