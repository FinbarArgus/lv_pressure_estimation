import os, sys
root_dir_path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(os.path.join(root_dir_path, 'python_ECG_tools'))
sys.path.append(os.path.join(root_dir_path, 'ultrasound_uncertainty_tools'))
sys.path.append(os.path.join(root_dir_path, 'circulatory_autogen'))
import pandas as pd
import numpy as np
import time
import json

from haemotools.BB_echo_functions import BBdata
from read_tomtec_worksheets import read_tomtec_worksheets

def get_needed_data_inv_and_tomtec(inv_data_path, tomtec_data_path,
                                        measurements_needed_inv, measurements_needed_tomtec, 
                                        nice_names_inv=None, nice_names_tomtec=None):
    """
    Creates a dict from the path to pickled invasive data file and csv tomtec data
    This dict only has the patients with all of the measurements in 
    measurements_needed_inv and measurements_needed_tomtec
    
    """

    if nice_names_inv in [[], None]:
        nice_names_inv = measurements_needed_inv
    if nice_names_tomtec in [[], None]:
        nice_names_tomtec= measurements_needed_tomtec
    nice_names_all = nice_names_inv + nice_names_tomtec
    
    # get inv data dict
    inv_dict = pd.read_pickle(inv_data_path)
    all_labels = ec.dict_counter(inv_dict)
    import pdb; pdb.set_trace()

    #get tomtec (echo) dataframe
    df = pd.read_csv(tomtec_data_path)
    df['patient_ID'].replace({'_':''}, regex=True, inplace=True)
    desc_df = pd.read_csv(tomtec_desc_path) 

    # get the patients that have the measurements we need
    patients_with_measurement = []
    for measurement_name in measurements_needed_inv:
        patients_with_measurement.append(all_labels[measurement_name]['idxs'])

    for measurement_name in measurements_needed_tomtec:
        patients_with_measurement.append([entry for entry in 
            df[~np.isnan(df[measurement_name])]['patient_ID'].to_list()])

    all_set = set.intersection(*[set(x) for x in patients_with_measurement])
    patients_with_all = list(all_set)
    # patients_with_all = list(set(patients_with_v_aov) & set(patients_with_D_aov)).sort()

    num_patients = len(patients_with_all)

    inv_needed_data = {}
    for patient_id in patients_with_all:
        inv_needed_data[patient_id] = {}
        for measurement_name, nice_name in zip(measurements_needed_inv, nice_names_inv):
            inv_needed_data[patient_id][nice_name] = []
            inv_needed_data[patient_id][nice_name+'_count'] = 0
            inv_needed_data[patient_id][nice_name+'_type'] = 'array'
            for Xnum_idx in inv_dict[patient_id].keys():
                if measurement_name in inv_dict[patient_id][Xnum_idx].keys():
                    inv_needed_data[patient_id][nice_name].append(inv_dict[patient_id][Xnum_idx][measurement_name])
                    inv_needed_data[patient_id][nice_name+'_count'] += 1

    print(inv_needed_data)
    needed_data = inv_needed_data

    tomtec_needed_data = df[df['patient_ID'].isin(patients_with_all)][['patient_ID'] + measurements_needed_tomtec]
    for patient_id in patients_with_all:
        for measurement_name, nice_name in zip(measurements_needed_tomtec, nice_names_tomtec):
            needed_data[patient_id][nice_name] = [tomtec_needed_data[tomtec_needed_data['patient_ID']==patient_id]
                    [measurement_name].iloc[0]]
            needed_data[patient_id][nice_name+'_count'] = 1
            needed_data[patient_id][nice_name+'_type'] = 'float'

    return needed_data, patients_with_all, nice_names_all, invasive_dt

if __name__ == '__main__':
    
    ec = BBdata()

    inv_data_path = '/eresearch/heart/farg967/Sandboxes/Stephen/Biobeat/IVP_data_test.pickle'
    tomtec_data_path = '/eresearch/heart/farg967/Sandboxes/Finbar/tomtec/tomtec_data.csv'
    tomtec_desc_path = '/eresearch/heart/farg967/Sandboxes/Finbar/tomtec/tomtec_desc.csv'

    # define 
    measurements_needed_inv = ['LV', 'AO']
    nice_names_inv = ['P_lv', 'P_ao'] # THese correspond to the above
    measurements_needed_tomtec = ['US.CA.LVOT.VMAX:ANTFLOW:DOPPLER', 'US.CA.LVOT.DIAM:BMODE', 'US.CA.AO.DIAM_STJ:BMODE']
    nice_names_tomtec = ['vel_aov', 'd_aov', 'd_ao'] # THese correspond to the above
    nice_names_all = nice_names_inv + nice_names_tomtec
    sample_rate = 240
    dt = 1/sample_rate

    print(f'getting data for the patients with this data')
    print(nice_names_all)

    data_dict, all_patient_ids, nice_measurement_names = get_needed_data_inv_and_tomtec(inv_data_path, tomtec_data_path, 
                                                    measurements_needed_inv, 
                                                    measurements_needed_tomtec, 
                                                    nice_names_inv=nice_names_inv, 
                                                    nice_names_tomtec=nice_names_tomtec)

    print(data_dict)
    num_patients = len(all_patient_ids)

    print(f'data dict for patients and needed measurements created')
    print(f'running analysis with {num_patients} patients')

    fig, ax = subfigure()

    for patient_id in all_patient_ids:
        for measurement in nice_measurement_names:
            for idx in range(data_dict[patient_id][measurement+'_count'])
                ax.plot(
