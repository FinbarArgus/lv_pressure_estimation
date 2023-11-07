import pandas as pd
import numpy as np
import time
import json
from matplotlib import pyplot as plt
import os
from get_valve_data import write_to_json_file

def create_gt_obs_data_Alfred(patient_num):

    # TODO the file paths should be inputs to this function
    data_dir_path = '/home/farg967/Documents/data/pulmonary'
    data_file_path = os.path.join(data_dir_path, 'Alfred_Echo_Pre_Post_vols_P1_13.csv')
    save_dir_path = '/home/farg967/Documents/data/pulmonary/ground_truth_for_CA'
    if not os.path.exists(save_dir_path):
        os.mkdir(save_dir_path)
    
    fs = 180
    
    # read csv file 
    df = pd.read_csv(data_file_path, delimiter=',') 

    df_row = df.iloc[np.where(df['Patient No'] == patient_num)]

    # turn df into dict
    data_dict = {patient_num : {entry: df_row[entry].values[0] for entry in df_row.columns}}

    # TODO get this from data file
    data_dict[patient_num]["P_ao Sys"] = 144
    data_dict[patient_num]["P_ao Dia"] = 101
    data_dict[patient_num]["P_pul Sys"] = 56
    # data_dict[patient_num]["P_pul Mean"] = 56
    data_dict[patient_num]["P_pul Dia"] = 20
    data_dict[patient_num]["P_rv Sys"] = 56
    # data_dict[patient_num]["P_pul Mean"] = 56
    data_dict[patient_num]["P_rv Dia"] = 7 
    data_dict[patient_num]["P_pcwp mean"] = 12

    ml_to_m3 = 1e-6
    mmHg_to_Pa = 133.332

    # TODO get the aortic pressure, rv pressure, and PA pressure from dataset here

    variables_of_interest_pre = [('Pre LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('Pre LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('P_ao Sys', 'ascending_aorta_B/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 3.0, 10.0, 'u_{ao}'),
                                ('P_ao Dia', 'ascending_aorta_B/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 3.0, 10.0, 'u_{ao}'),
                                ('P_pul Sys', 'MPA_A/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{pul}'),
                                ('P_pul Dia', 'MPA_A/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{pul}'),
                                ('P_rv Sys', 'heart/u_rv', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{rv}'),
                                ('P_rv Dia', 'heart/u_rv', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{rv}'),
                                ('P_pcwp mean', 'heart/u_la', 'mean', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{la}')]

    variables_of_interest_post = [('Post LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('Post LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('P_ao Sys', 'brachial_L82/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 3.0, 10.0, 'u_{ao}'),
                                ('P_ao Dia', 'brachial_L82/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 3.0, 10.0, 'u_{ao}'),
                                ('P_pul Sys', 'MPA_A/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{pul}'),
                                ('P_pul Dia', 'MPA_A/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{pul}'),
                                ('P_rv Sys', 'heart/u_rv', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{rv}'),
                                ('P_rv Dia', 'heart/u_rv', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{rv}'),
                                ('P_pcwp mean', 'heart/u_la', 'mean', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{la}')]
                                    
    # add stroke volume here
    constants_of_interest_pre = [('Pre SV (ml)', 'SV_lv',
                            'm3', ml_to_m3, 'Alfred_database')]
    
    save_name = 'ground_truth_Alfred'
    save_name_pre = save_name + '_pre'
    write_to_json_file(data_dict, variables_of_interest_pre, constants_of_interest_pre,
                    save_dir_path, save_name=save_name_pre, sample_rate=fs)

    # combine periods json constants file with the one just generated for the pre case
    periods_file = os.path.join(save_dir_path, f'alfred_periods_constants_{patient_num}.json')

    with open(os.path.join(save_dir_path, f'{save_name_pre}_constants_{patient_num}.json'), 'r') as file_1:
        data_1 = json.load(file_1)
    
    with open(os.path.join(save_dir_path, periods_file), 'r') as file_2:
        data_2 = json.load(file_2)

    # also add vessel geometry information
    geom_file_pre = os.path.join(save_dir_path, f'ROM_gt/vessel_geom_constants_pre_patient_{patient_num}.json')
    geom_file_post = os.path.join(save_dir_path, f'ROM_gt/vessel_geom_constants_post_patient_{patient_num}.json')
    
    with open(os.path.join(save_dir_path, geom_file_pre), 'r') as file_3_pre:
        data_3_pre = json.load(file_3_pre)
    
    with open(os.path.join(save_dir_path, geom_file_post), 'r') as file_3_post:
        data_3_post = json.load(file_3_post)

    # ths only works because my json data is a list
    combined_data_pre = data_1 + data_2 + data_3_pre
    # post case still has periods from pre, because we assume they are unknown for post
    combined_data_post = data_1 + data_2 + data_3_post

    with open(os.path.join(save_dir_path, f'{save_name}_pre_constants_{patient_num}.json'), 'w') as wf:
        json.dump(combined_data_pre, wf, indent=2)
    
    with open(os.path.join(save_dir_path, f'{save_name}_post_constants_{patient_num}.json'), 'w') as wf:
        json.dump(combined_data_post, wf, indent=2)


if __name__ == '__main__':
        
    if len(sys.argv) == 2:
        patient_num=sys.argv[1]
        
    else:
        print("usage:  python create_gt_Alfred.py patient_num") 
        exit()
