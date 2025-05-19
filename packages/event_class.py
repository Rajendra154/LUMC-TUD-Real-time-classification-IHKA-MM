# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which contains the class for events
Version: 0.3.0 - 07-03-2024
"""

import numpy as np
import math

class event:
    def __init__(self, spike_marker, i):
        self.start_sample = spike_marker[0]
        self.start_sec = math.floor(self.start_sample/1000)
        self.start_sample_i = i
        self.num_spikes = 1
        self.ave_pos_peak = spike_marker[1]
        self.ave_neg_peak = spike_marker[2]
        self.spike_per_sec = [1]
        self.five_second_spike = np.empty((0,4), float)
        self.max_five_second_spike = 0
        self.update_five_second_spike(spike_marker)
        self.spikes_included = [spike_marker[0]]
        
    def update_spike_per_sec(self, cur_spike):
        cur_sec = math.floor(cur_spike/1000)
        while((cur_sec-self.start_sec+1)>len(self.spike_per_sec)):
            self.spike_per_sec = np.append(self.spike_per_sec, [0])
        self.spike_per_sec[cur_sec-self.start_sec] += 1
    
    def update_five_second_spike(self, spike_marker):
        while 1:
            if((len(self.five_second_spike) > 0) and (spike_marker[0] - self.five_second_spike[0][0] > 5000)):
                self.five_second_spike = np.delete(self.five_second_spike, 0, axis=0)
            else:
                break
        
        self.five_second_spike = np.append(self.five_second_spike, spike_marker.reshape(1,4), axis=0)
        five_second_len = len(self.five_second_spike)
        if(five_second_len>self.max_five_second_spike):
            self.max_five_second_spike = five_second_len            
            
    def check_new_frequency(self, spike_marker, minimum_freq):
        if(spike_marker[0]!=self.start_sample):
            cur_freq = ((self.num_spikes+1)*1000)/(spike_marker[0]-self.start_sample)
            if(cur_freq >= minimum_freq):
                self.frequency = cur_freq
                self.num_spikes += 1
                self.spikes_included.append(spike_marker[0])
                self.ave_pos_peak = self.ave_pos_peak + (spike_marker[1]-self.ave_pos_peak)/self.num_spikes
                self.ave_neg_peak = self.ave_neg_peak + (spike_marker[2]-self.ave_neg_peak)/self.num_spikes
                self.update_spike_per_sec(spike_marker[0])
                self.update_five_second_spike(spike_marker)
                return True
        return False
        
    def define_end_event(self, last_spike, last_i):
        self.stop_sample = last_spike
        self.stop_sample_i = last_i
        self.min_freq = min(self.spike_per_sec)
        self.max_freq = max(self.spike_per_sec)
        
    def classify_event(self, input_variables):
        self.classification = 0
        if(self.max_five_second_spike > input_variables.min_hpd_freq):
            if(self.stop_sample-self.start_sample > input_variables.min_ictal_hpd_duration):
                self.classification = 2
            elif(self.stop_sample-self.start_sample > input_variables.min_event_duration):
                self.classification = 1
        elif(self.stop_sample - self.start_sample > input_variables.max_hvsw_duration):
            self.classification = 2
            
    def check_preliminary_spikes(self, spike_marker, spike_min_amp, minimum_freq):
        check_min_freq = False
        checked = False
        if(self.min_freq > 0):
            pre_spikes_per_sec = np.zeros(1,int)
            check_min_freq = True
        while 1:
            if(self.start_sample_i-1<=0):
                break
            if(self.start_sample-spike_marker[self.start_sample_i-1][0]<3000):
                cur_freq = ((self.num_spikes+1)*1000)/(self.stop_sample-spike_marker[self.start_sample_i-1][0])
                if(cur_freq>=minimum_freq):
                    self.start_sample = spike_marker[self.start_sample_i-1][0]
                    self.start_sample_i -= 1
                    self.frequency = cur_freq
                    self.num_spikes += 1
                    self.ave_pos_peak = self.ave_pos_peak + (spike_marker[self.start_sample_i-1][1]-self.ave_pos_peak)/self.num_spikes
                    self.ave_neg_peak = self.ave_neg_peak + (spike_marker[self.start_sample_i-1][2]-self.ave_neg_peak)/self.num_spikes
                    self.spikes_included.append(spike_marker[self.start_sample_i][0])
                    if(check_min_freq):
                        checked = True
                        cur_sec = math.floor(self.start_sample/1000)
                        while((self.start_sec-cur_sec+1)>len(pre_spikes_per_sec)):
                            pre_spikes_per_sec = np.insert(pre_spikes_per_sec, 0, [0])
                        pre_spikes_per_sec[0] += 1
                else:
                    break
            else:
                break
        
        if(checked and self.min_freq>min(pre_spikes_per_sec)):
            self.min_freq = min(pre_spikes_per_sec)
        self.start_sec = math.floor(self.start_sample/1000)
        