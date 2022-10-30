import os, sys
root_dir_path = os.path.join(os.path.dirname(__file__), '../')
parent_dir_path = os.path.join(os.path.dirname(__file__), '../../')
import pandas as pd
import numpy as np
import time
import json
from matplotlib import pyplot as plt
    
plot_dir = os.path.join(root_dir_path, 'images')
data_path = '/eresearch/heart/farg967/Sandboxes/Finbar/combined/reduced_data.pkl'
data_dict = pd.read_pickle(data_path).to_dict()
print(data_dict)
all_patients = list(data_dict.keys())

sample_rate = 240
dt = 1/sample_rate

systolic_idx = 100

b_matrix = np.array([data_dict[patient_id]['P_lv'][:systolic_idx] - 
        data_dict[patient_id]['P_ao'][:systolic_idx] for 
        patient_id in all_patients])

b = b_matrix.flatten()

flow_matrix = np.array([np.ones(systolic_idx)*data_dict[patient_id]['vel_aov']*data_dict[patient_id]['d_aov']**2/4 for patient_id in all_patients])

A = flow_matrix.reshape([-1, 1])

theta = np.linalg.lstsq(A, b)

R= theta[0]

P_lv = np.array([data_dict[patient_id]['P_lv'][:systolic_idx] for patient_id in all_patients])
P_ao = np.array([data_dict[patient_id]['P_ao'][:systolic_idx] for patient_id in all_patients])
P_ao_pred = P_lv - R*flow_matrix

for II in range(len(P_ao)):
    fig, ax = plt.subplots()
    ax.plot(P_ao[II], 'k', label='measured')
    ax.plot(P_ao_pred[II], 'b', label='predicted')
    ax.legend()
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    plt.savefig(os.path.join(plot_dir, f'P_ao_pred_comparison_{all_patients[II]}'))
    plt.close()
        




