# -*- coding: utf-8 -*-
"""
@author: Jeroen Vermeulen
@institute: TU Delft, Quantum and Computer Engineering
@description: File which contains general function for plotting results
Version: 0.3.0 - 07-03-2024
"""

import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from packages.neo_impl import threshold_calc_detect
from packages.activity import detect_activity

# CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
#                   '#f781bf', '#a65628', '#984ea3',
#                   '#999999', '#e41a1c', '#dede00']

vspan_list = []

# Plot the data with spikes and activity if available
def plot_data(title, input_eeg, spike_data, eeg_base, eeg_iir, neo_iir, events, threshold_constant, ymax, ymin, xsize):
    thresh_adjust = False
    
    alpha_var = .5
    Plot, Axis = plt.subplots(figsize=(15, 5))
    x_scale = np.arange(0, len(input_eeg)/1000, 1/1000)
    
    if(eeg_iir is not None and neo_iir is not None):
        thresh_adjust = True
        plt.subplots_adjust(bottom=.3)
    else:
        plt.subplots_adjust(bottom=.25)
        
    plt.plot(x_scale, input_eeg, color = '#377eb8')
    Axis.grid(axis = 'y')
    spike_plot, = Axis.plot(x_scale, spike_data.T[1], color = '#e41a1c')
    plt.title(title[1:len(title)])
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [mV]')
    
    if(events is not None):
        hvsw_label = mpatches.Patch(color='#4daf4a', alpha=alpha_var, label='HVSW')
        shpd_label = mpatches.Patch(color='#ff7f00', alpha=alpha_var, label='sHPD')
        ihpd_label = mpatches.Patch(color='#dede00', alpha=alpha_var, label='iHPD')
        spike_train_label = mpatches.Patch(color='#984ea3', alpha=alpha_var, label='spike train')
        plt.legend(handles=[hvsw_label,shpd_label,ihpd_label,spike_train_label], loc='upper right')
        for i in range(len(events)):
            if(events[i][8] == 3):
                vspan_list.append(Axis.axvspan(events[i][0]/1000, events[i][1]/1000, color='#984ea3', alpha=alpha_var))
            elif(events[i][8] == 2):
                vspan_list.append(Axis.axvspan(events[i][0]/1000, events[i][1]/1000, color='#dede00', alpha=alpha_var))
            elif(events[i][8] == 1):
                vspan_list.append(Axis.axvspan(events[i][0]/1000, events[i][1]/1000, color='#ff7f00', alpha=alpha_var))
            else:
                vspan_list.append(Axis.axvspan(events[i][0]/1000, events[i][1]/1000, color='#4daf4a', alpha=alpha_var))

    max_pos = round(len(spike_data.T[0])/1000)
    
    if(thresh_adjust):
        scroll_slider_position = plt.axes([0.2, 0.15, 0.65, 0.03], facecolor = 'White')
    else:
        scroll_slider_position = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor = 'White')
        
    scroll_slider = Slider(scroll_slider_position, 'Position', 0, max_pos, valinit=0)

    def update_scroll_slider(val):
        pos = scroll_slider.val
        Axis.axis([pos, pos+xsize, ymin, ymax])
        Plot.canvas.draw_idle()
        
    def update_thresh_slider(val):
        threshold_constant = thresh_slider.val

    def scroll(event):
        if(xsize > 5):
            scale = 5
        else:
            scale = xsize
        update = False
        if(event.button == 'up' and Axis.get_xlim()[0]<=max_pos):
            pos = Axis.get_xlim()[0] + scale
            update = True
        elif(event.button == 'down' and Axis.get_xlim()[0]!=0):
            pos = Axis.get_xlim()[0] - scale
            update = True
        if(update):
            Axis.axis([pos, pos+xsize, ymin, ymax])
            Plot.canvas.draw_idle()
            scroll_slider.set_val(pos)
        
    def slide(event):
        if(xsize > 5):
            scale = 5
        else:
            scale = xsize
        update = False
        if(event.key == 'right' and Axis.get_xlim()[0]<=max_pos):
            pos = Axis.get_xlim()[0] + scale
            update = True
        elif(event.key == 'left' and Axis.get_xlim()[0]!=0):
            pos = Axis.get_xlim()[0] - scale   
            update = True
        elif(event.key == 'up'):
            if(thresh_adjust):
                print('Rerunning spike detection with threshold:', thresh_slider.val)
                spike_marker, spike_over_time, exclusion = threshold_calc_detect(input_eeg, eeg_base, eeg_iir, neo_iir, thresh_slider.val)
                if(events is not None):
                    detect_event, event_over_time, spikes_amp_marked = detect_activity(eeg_base, spike_marker)
                    for vspan in vspan_list:
                        vspan.remove()
                    vspan_list.clear()
                    for i in range(len(detect_event)):
                        if(detect_event[i][8] == 2):
                            vspan_list.append(Axis.axvspan(detect_event[i][0]/1000, detect_event[i][1]/1000, color='#dede00', alpha=alpha_var))
                        elif(detect_event[i][8] == 1):
                            vspan_list.append(Axis.axvspan(detect_event[i][0]/1000, detect_event[i][1]/1000, color='#ff7f00', alpha=alpha_var))
                        else:
                            vspan_list.append(Axis.axvspan(detect_event[i][0]/1000, detect_event[i][1]/1000, color='#4daf4a', alpha=alpha_var))
                spike_plot.set_ydata(spike_over_time.T[1])
                plt.draw()
                print('Done with:', thresh_slider.val)
        if(update):
            Axis.axis([pos, pos+xsize, ymin, ymax])
            Plot.canvas.draw_idle()
            scroll_slider.set_val(pos)
            
    if(thresh_adjust):
        thresh_slider_position = plt.axes([0.2, 0.05, 0.65, 0.03], facecolor = 'White')
        thresh_slider = Slider(thresh_slider_position, 'Spike threshold', 2, 40, valinit=threshold_constant, valstep=0.1)
        thresh_slider.on_changed(update_thresh_slider)
        
    scroll_slider.on_changed(update_scroll_slider)
    Plot.canvas.mpl_connect('scroll_event', scroll) 
    Plot.canvas.mpl_connect('key_press_event', slide) 

    update_scroll_slider(0)
    plt.show()