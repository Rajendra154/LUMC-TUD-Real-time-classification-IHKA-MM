# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which opens a figure from existing results
Version: 0.3.0 - 07-03-2024
"""

import tkinter
import os
import scipy.io
import numpy as np
import mat73
from tkinter import filedialog
from packages.plotting import plot_data

root = tkinter.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()

folder_path = filedialog.askdirectory(parent=root)
file_name = os.path.basename(os.path.normpath(folder_path))
file_name = r'/'+file_name[0:len(file_name)-8]

try:
    eeg_data = scipy.io.loadmat(os.path.dirname(folder_path)+'/'+file_name+'.mat')
    eeg_data = eeg_data['data'].T[0].T
except:
    eeg_data = mat73.loadmat(os.path.dirname(folder_path)+'/'+file_name+'.mat')
    eeg_data = eeg_data['data']

if os.path.exists(folder_path+'/'+file_name+'_activity.mat'):
    event_file = scipy.io.loadmat(folder_path+'/'+file_name+'_activity.mat', simplify_cells=True)
    event_length = len(event_file['start_sample'])
    events = np.empty((event_length,0), float)
    for i in event_file:
        if(i!='__header__' and i!='__version__' and i!='__globals__'):
            events = np.append(events, event_file[i].reshape(event_length,1),axis=1)
else:
    events = None


spikes = np.empty((0,4), float)

j = 1
while(1):
    if not os.path.exists(folder_path+'/'+file_name+'_an_hr_'+str(j)+'.mat'):
        break
    
    spike_file = scipy.io.loadmat(folder_path+'/'+file_name+'_an_hr_'+str(j)+'.mat', simplify_cells=True)
    spike_length = len(spike_file['time'])
    spike_snippet = np.empty((spike_length,0), float)
    spike_snippet = np.append(spike_snippet, spike_file['time'].reshape(spike_length,1), axis=1)
    spike_snippet = np.append(spike_snippet, spike_file['all_spikes'].reshape(spike_length,1), axis=1)
    spike_snippet = np.append(spike_snippet, spike_file['pos_amplitude'].reshape(spike_length,1), axis=1)
    spike_snippet = np.append(spike_snippet, spike_file['neg_amplitude'].reshape(spike_length,1), axis=1)
    spikes = np.append(spikes, spike_snippet.reshape(spike_length,4), axis=0)
    j+=1

# Limit variable for plotting: amplitude for y-axis and amount of seconds shown on x-axis
ymax = 6
ymin = -6
xsize = 30

if(len(eeg_data) < len(spikes)):
    spikes = spikes[0:len(eeg_data)]
if(len(spikes) < len(eeg_data)):
    eeg_data = eeg_data[0:len(spikes)]

plot_data(file_name, eeg_data, spikes, None, None, None, events, None, ymax, ymin, xsize)
