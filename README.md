# LUMC-TUD-Real-time-classification-IHKA-MM
Real-Time Classification of Epileptiform Activity in the Intrahippocampal Kainic Acid Mouse Model: Master Thesis Jeroen Vermeulen

# Abstract
One-third of patients suffering from chronic epilepsy, which is caused by abnormal brain activity, is
drug-resistant. Animal models are widely used to study the mechanisms leading to epilepsy so better
drug treatments can be developed for this disease. In such studies, epileptiform activity, assessed by
LFP recordings, can be used as a marker for the development and chronification of disease. However,
the analysis of LFP recordings is typically done manually, which is time-consuming, subject to observer
bias, error-prone, and lacks consistency and efficiency. Therefore, we present a work which developed
a new, automated detection and classification method for epileptiform activity, which was tested in the
intrahippocampal kainic acid (IHKA) mouse model, a model of human temporal lobe epilepsy. Our
method relies on a spike detector using an improved version of the nonlinear energy operator (NEO) in
combination with automatic NEO thresholding (ANT). The detected spikes form the basis of epileptiform
event detection and classification. The proposed method is implemented in Python as an automated
and time-efficient algorithm that can be used in preclinical studies. Epileptiform event detection accuracy
was 93.1% and classification accuracy 95.8%. Moreover, the time for analysis of LFP recordings
was reduced by 98.8% compared to manual analysis. Additionally, to demonstrate the potential of the
algorithm for application in Brain-Machine Interfaces (BMI), we performed a real-time implementation
using both an application-specific integrated circuit (ASIC) and a field programmable gate array (FPGA).
The FPGA demonstrated the feasibility of real-time implementation, and the ASIC resulted in an area
and power efficient chip using the Taiwan semiconductor manufacturing company (TSMC) 45nm library
that constitutes a post-layout area of 9114 μm2 and a power usage of 6.11 μW.

# Spike and Activity detection Python code Manual
Author: Jeroen Vermeulen, Institute: TU Delft, Quantum and Computer Engineering
V0.3.0 – 07-03-2024

How to use the code:
1.	Download the python files from the repository; the files can be placed anywhere.
2.	Download Anaconda https://www.anaconda.com/download 
  a.	All the needed packages should be automatically installed. 
3.	Open Anaconda and from the menu that pops-up open Spyder, in Spyder:
  a.	From the top left file->open. open the three python files: spike_detection.py, spike_activity_detection.py, open_figure.py
4.	Before running make sure you have once changed the following setting for the figure to open in a separate window, this is necessary to be able to scroll.
  a.	From Tools->Preferences->IPython console->Graphics->Graphics backend and chose Automatic
5.	The file ‘spike_detection.py’ will run the spike detection, open a figure and save the spike information. The file ‘spike_activity_detection.py’ will next to spike detection also runs activity detection and all the data will be shown in the figure and be saved. At last ‘open_figure.py’ will open a figure from already generated and saved results.
Running both files is a similar procedure:
  a.	Define a directory where the input file resides.
  b.	If you only wish to run one file uncomment the section below ‘when using one file uncomment below’ and comment the part below ‘When using loop through folder uncomment below’. A file name needs to be defined like ‘r\KA7_230516_063714_1122_HCr1rACa’, in front of the apostrophe the r needs to be included, inside the apostrophe start with a backwards slash and do not include .mat
  c.	If you only wish to run through a folder uncomment the section below below ‘When using loop through folder uncomment below’ and comment the part below ‘when using one file uncomment below’.
6.	Running the file is done by pressing the start button in the top bar or pressing ctrl+enter. The code takes around 90 to 150 seconds to run.
  a.	If the error: “ModuleNotFoundError: No module named 'packages'” occurs, make sure in the top right corner the working directory is chosen to be the directory where the python files spike_detection.py and spike_activity_detection.py are in.

7.	A few settings can be changed to alter the working, this will be described below:
  a.	In spike_detection.py, spike_activity_detection.py and open_figure.py the viewing area can be changed with: ymax and ymin, determing the y-axis scale and xsize, determining the time in seconds which is shown.
  b.	In ‘spike_detection.py’: spike_threshold can be changed which changes the sensitivity with which spikes are detected. Lower is more spikes detected.
  c.	In ‘spike_activity_detection.py’:
    i.	Spike_threshold can be changed like in ‘spike_detection.py’
    ii.	Amplitude_times_baseline: the minimal amplitude with which spikes are included in events. The value given will be multiplied by the baseline amplitude. Standard value 2
    iii.	Min_event_freq: minimum frequency with which spikes need to occur in an event. standard value 2(Hz)
    iv.	Min_hpd_freq: minimum frequency with which spikes need to occur for an event to be classified as HPD. The algorithm will measure the highest frequency for 5 seconds and compare with this value. Standard value 4(Hz)
    v.	Min_spike_train_duration: minimum duration of a group of spikes to be marked as spike train. Standard value 2(s)
    vi.	Min_event_duration: minimum duration of an event to be detected. standard value 5(s)
    vii.	Min_ictal_hpd_duration: minimum duration of an HPD event to be classified as ictal. Standard value 10(s)
    viii.	Max_hvsw_duration: maximal duration of an HVSW event, if longer the event will be automatically classified as HPD. Standard value 10(s)
    ix.	Min_inter_event: minimal inter event time, if shorter or equal events are joined. Standard value 3(s)
8.	When results are already generated, open_figure.py can be run by simply double pressing the file in its folder or via the same way as the other files.

