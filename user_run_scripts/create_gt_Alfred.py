import pandas as pd
import numpy as np
import time
import json
from matplotlib import pyplot as plt
import os
from get_valve_data import write_to_json_file

def create_gt_obs_data_Alfred(patient_num):

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

    # TODO remove this when I actually have pressure
    data_dict[patient_num]["P Sys"] = 120
    data_dict[patient_num]["P Dia"] = 80

    ml_to_m3 = 1e-6
    mmHg_to_Pa = 133.332

    variables_of_interest_pre = [('Pre LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('Pre LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('P Sys', 'brachial_L82/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{br}'),
                                ('P Dia', 'brachial_L82/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{br}')]

    variables_of_interest_post = [('Post LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('Post LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                    'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                ('P Sys', 'brachial_L82/u', 'max', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{br}'),
                                ('P Dia', 'brachial_L82/u', 'min', 
                                    'J_per_m3', mmHg_to_Pa, 1.0, 10.0, 'u_{br}')]
                                    
    # add stroke volume here
    constants_of_interest_pre = [('Pre SV (ml)', 'SV_lv',
                            'm3', ml_to_m3, 'Alfred_database')]
    constants_of_interest_post = [('Post SV (ml)', 'SV_lv',
                            'm3', ml_to_m3, 'Alfred_database')]
    
    save_name = 'ground_truth_Alfred_Pre'
    write_to_json_file(data_dict, variables_of_interest_pre, constants_of_interest_pre,
                    save_dir_path, save_name=save_name, sample_rate=fs)

    write_to_json_file(data_dict, variables_of_interest_post, constants_of_interest_post,
                    save_dir_path, save_name=save_name, sample_rate=fs)

    # combine periods json constants file with the one just generated
    periods_file = os.path.join(save_dir_path, f'alfred_periods_constants_{patient_num}.json')

    with open(os.path.join(save_dir_path, f'{save_name}_constants_{patient_num}.json'), 'r') as file_1:
        data_1 = json.load(file_1)
    
    with open(os.path.join(save_dir_path, periods_file), 'r') as file_2:
        data_2 = json.load(file_2)

    # ths only works because my json data is a list
    combined_data = data_1 + data_2

    with open(os.path.join(save_dir_path, f'{save_name}_constants_{patient_num}.json'), 'w') as wf:
        json.dump(combined_data, wf, indent=2)


if __name__ == '__main__':
        
    if len(sys.argv) == 2:
        patient_num=sys.argv[1]
        
    else:
        print("usage:  python create_gt_Alfred.py patient_num") 
        exit()
