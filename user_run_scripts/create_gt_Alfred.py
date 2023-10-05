import pandas as pd
import numpy as np
import time
import json
from matplotlib import pyplot as plt
import os
from get_valve_data import write_to_json_file

if __name__ == '__main__':

    data_dir_path = '/home/farg967/Documents/data/pulmonary'
    data_file_path = os.path.join(data_dir_path, 'Alfred_Echo_Pre_Post_vols_P1_13.csv')
    save_dir_path = '/home/farg967/Documents/data/pulmonary/ground_truth_for_CA'
    if not os.path.exists(save_dir_path):
        os.mkdir(save_dir_path)

    patient_no = 3
    
    # read csv file
    df = pd.read_csv(data_file_path, delimiter=',')

    print(df)

    df_row = df.iloc[np.where(df['Patient No'] == patient_no)]

    # TODO make this automatically go from df to dict
    data_dict = {patient_no : {'Pre LV Dia Vol- ml' : df_row['Pre LV Dia Vol- ml'].values[0],
                               'Pre LV Sys Vol- ml' : df_row['Pre LV Sys Vol- ml'].values[0],
                               'Post LV Dia Vol- ml' : df_row['Post LV Dia Vol- ml'].values[0],
                               'Post LV Sys Vol- ml' : df_row['Post LV Sys Vol- ml'].values[0],
    }}

    ml_to_m3 = 1e-6

    variables_of_interest_pre = [('Pre LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                      'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                  ('Pre LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                      'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}')]

    variables_of_interest_post = [('Post LV Dia Vol- ml', 'heart/q_lv', 'max', 
                                      'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}'),
                                  ('Post LV Sys Vol- ml', 'heart/q_lv', 'min', 
                                      'm3', ml_to_m3, 1.0, 10.0, 'q_{lv}')]
    # add stroke volume here
    constants_of_interest_pre = []
    constants_of_interest_post= []
    
    write_to_json_file(data_dict, variables_of_interest_pre, constants_of_interest_pre,
                       save_dir_path, save_name='ground_truth_Alfred_Pre', sample_rate=240.0)

    write_to_json_file(data_dict, variables_of_interest_post, constants_of_interest_post,
                       save_dir_path, save_name='ground_truth_Alfred_Post', sample_rate=240.0)
