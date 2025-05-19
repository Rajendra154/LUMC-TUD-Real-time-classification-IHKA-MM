# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which runs spike detection, saves and plots the results
Version: 0.3.0 - 07-03-2024
"""

import os
from packages.neo_impl import run_spike_detection
from packages.utilities import save_results
from packages.plotting import plot_data

# Define input folder
directory = r'C:\Users\MANASI\OneDrive - Delft University of Technology\Documents\TUD_Thesis\Research_phase\Share with Manasi\Input_files'

# Limit variable for plotting: amplitude for y-axis and amount of seconds shown on x-axis
ymax = 6
ymin = -6
xsize = 10

# Variable to adjust the sensitivity of spike detection, lower is more sensitive is more spikes
spike_threshold = 14

#######################################
# When using one file uncomment below #
#######################################

# file_name = r'\KA7_230516_063714_1122_HCr1rACa'
# spikes, base_eeg, spike_over_time, input_eeg, exclusion, eeg_iir, neo_iir = run_spike_detection(directory, file_name, spike_threshold)
# plot_data(file_name, input_eeg, spike_over_time, base_eeg, eeg_iir, neo_iir, None, spike_threshold, ymax, ymin, xsize)
# save_results(directory, file_name, input_eeg, spikes, spike_over_time, None, None, exclusion)

 
##################################################
# When using loop through folder uncomment below #
##################################################

for name in os.listdir(directory):
    if name.endswith('.mat'):
        file_name = '/' + name[0:len(name)-4]
        spikes, base_eeg, spike_over_time, input_eeg, exclusion, eeg_iir, neo_iir = run_spike_detection(directory, file_name, spike_threshold)
        save_results(directory, file_name, input_eeg, spikes, spike_over_time, None, None, exclusion)
        print(name[0:len(name)-4], 'done')
