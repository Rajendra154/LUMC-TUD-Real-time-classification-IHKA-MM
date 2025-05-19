# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which runs spike detection and activity detection, saves and plots the results
Version: 0.3.0 - 07-03-2024
"""

import os
from packages.neo_impl import run_spike_detection
from packages.activity import detect_activity
from packages.utilities import save_results, activity_variables
from packages.plotting import plot_data

#Define input
directory = r'C:\Users\MANASI\OneDrive - Delft University of Technology\Documents\TUD_Thesis\Research_phase\Share with Manasi\Input_files'

# Limit variable for plotting: amplitude for y-axis and amount of seconds shown on x-axis
ymax = 6
ymin = -6
xsize = 30

# Variable to adjust the sensitivity of spike detection, lower is more sensitive is more spikes
spike_threshold             = 14

# Input variables for the detection of spikes, detection of events and classification of events
amplitude_times_baseline    = 2

min_event_freq              = 2
min_hpd_freq                = 4

min_spike_train_duration    = 2
min_event_duration          = 5
min_ictal_hpd_duration      = 10
max_hvsw_duration           = 10
min_inter_event             = 3

activity_variables = activity_variables(amplitude_times_baseline, min_event_freq, min_hpd_freq*5, min_spike_train_duration*1000, min_event_duration*1000,
                                     min_ictal_hpd_duration*1000, max_hvsw_duration*1000, min_inter_event*1000)

#######################################
# When using one file uncomment below #
#######################################

# file_name = r'\KA7_230516_063714_1122_HCr1rACa'
# spikes, base_eeg, spike_over_time, input_eeg, exclusion, eeg_iir, neo_iir = run_spike_detection(directory, file_name, spike_threshold)
# events, event_over_time, spikes_amp_marked = detect_activity(base_eeg, spikes, activity_variables)
# plot_data(file_name, input_eeg, spike_over_time, base_eeg, eeg_iir, neo_iir, events, spike_threshold, ymax, ymin, xsize)
# save_results(directory, file_name, input_eeg, spikes_amp_marked, spike_over_time, events, event_over_time, exclusion)


##################################################
# When using loop through folder uncomment below #
##################################################

for name in os.listdir(directory):
    if name.endswith('.mat'):
        file_name = '/' + name[0:len(name)-4]
        spikes, base_eeg, spike_over_time, input_eeg, exclusion, eeg_iir, neo_iir = run_spike_detection(directory, file_name, spike_threshold)
        events, event_over_time, spikes_amp_marked = detect_activity(base_eeg, spikes, activity_variables)
        save_results(directory, file_name, input_eeg, spikes_amp_marked, spike_over_time, events, event_over_time, exclusion)
        print(name[0:len(name)-4], 'done')


