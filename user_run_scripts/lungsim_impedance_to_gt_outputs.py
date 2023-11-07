import json
import pandas as pd
import sys
import os

def convert_lungsim_output_to_obs_data_json(patient_num, pre_or_post, project_dir):

    data_file_path = os.path.join(project_dir, f'data/pulmonary/lobe_impedances/{patient_num}/{pre_or_post}/lobe_imped.json')
    vessel_array_path = os.path.join(project_dir, f"physiology_models/pulmonary_CVS_Alfred/patient_{patient_num}/{pre_or_post}/resources/lung_ROM_vessel_array.csv")
    save_file_path = os.path.join(project_dir, f'data/pulmonary/ground_truth_for_CA/ROM_gt/lung_ROM_lobe_imped_{pre_or_post}_patient_{patient_num}_obs_data.json')
    constants_save_file_path = os.path.join(project_dir, f'data/pulmonary/ground_truth_for_CA/ROM_gt/vessel_geom_constants_{pre_or_post}_patient_{patient_num}.json')

    with open(data_file_path, 'r') as file:
        data = json.load(file)

    vessel_array = pd.read_csv(vessel_array_path, index_col=0)
    # dyne_s_per_cm5_to_J_s_per_m6 
    conversion = 1e5

    mean_flow = 8e-5 # TODO this might be changed

    approx_downstream_resistance_ratio = 0.35 # TODO make this exact from the radii/lengths

    full_dict = {}
    entry_list = []
    constant_list = []
    terminal_names = []
    for II in range(len(data["vessel_names"])):
        # get radius and length entries
        radius_entry = {}
        radius_entry["variable_name"] = f'r_{data["vessel_names"][II]}'
        radius_entry["units"] = 'metre'
        if data['radius']['unit'] == 'mm':
            const_conversion = 1e-3
        elif data['radius']['unit'] == 'metre':
            const_conversion = 1
        else:
            print('unit of', data['radius']['unit'], 'is not implemented') 
            exit()
        radius_entry["value"] = const_conversion*data['radius'][data["vessel_names"][II]][0]
        radius_entry["data_reference"] = 'Alfred_database'
        
        length_entry = {}
        length_entry["variable_name"] = f'l_{data["vessel_names"][II]}'
        length_entry["units"] = 'metre'
        if data['Length']['unit'] == 'mm':
            const_conversion = 1e-3
        elif data['Length']['unit'] == 'metre':
            const_conversion = 1
        else:
            print('unit of', data['Length']['unit'], 'is not implemented') 
            exit()
        # TODO This is temporary until Behdad gives updated MPA LPA RPA lengths
        # TODO 
        # TODO
        # TODO remove the below if statement!!!
        if data["vessel_names"][II].startswith("MPA"):
            length_entry["value"] = 4    *      const_conversion*data['Length'][data["vessel_names"][II]][0]
        elif data["vessel_names"][II].startswith("LPA") or data["vessel_names"][II].startswith("RPA"):
            length_entry["value"] = 3     *      const_conversion*data['Length'][data["vessel_names"][II]][0]
        else:
            length_entry["value"] = const_conversion*data['Length'][data["vessel_names"][II]][0]
        length_entry["data_reference"] = 'Alfred_database'

        constant_list.append(radius_entry)
        constant_list.append(length_entry)

        arteries_to_skip = ["MPA_A", "LPA_A", "RPA_A", "RBS_A", "LBS_A"] # []
        terminals = ["LLL", "LUL", "RLL", "RML", "RUL"]
        
        entry = {}
        entry["variable"] = data["vessel_names"][II]
        if entry["variable"].endswith("_V"):
            # Temporarily skip the venous vessel data
            continue
        
        if entry["variable"] not in arteries_to_skip:
            # terminals
            resistance_entry = {}
            terminal_name = data["vessel_names"][II].replace('_A', '')
            resistance_entry["variable_name"] = f'R_T_{terminal_name}'
            resistance_entry["units"] = 'Js_per_m6'
            resistance_entry["data_reference"] = 'Alfred_database'
            resistance_entry["value"] = conversion*data["impedance"][data["vessel_names"][II]][0]*(1-approx_downstream_resistance_ratio)
            constant_list.append(resistance_entry)


        entry["data_type"] = "frequency"
        entry["operation"] = "division"
        input_vessel = vessel_array["inp_vessels"][data["vessel_names"][II]].strip()
        BC_type = vessel_array["BC_type"][data["vessel_names"][II]].strip()
        if BC_type.startswith("p"):
            entry["operands"] = [f'{input_vessel}/u',
                                 f'{data["vessel_names"][II]}/v']
        else:
            entry["operands"] = [f'{data["vessel_names"][II]}/u',
                                 f'{input_vessel}/v']

        entry["unit"] = "Js/m^6" # data["impedance"]["unit"]
        entry["obs_type"] = "frequency"
        entry["value"] = [val*conversion for val in data["impedance"][data["vessel_names"][II]]]
        entry["std"] = [conversion*val/10 for val in data["impedance"][data["vessel_names"][II]]]
        entry["frequencies"] = data["frequency"]
        entry["phase"] = [-val for val in data["phase"][data["vessel_names"][II]]] # IMPORTANT phase is multiplied by negative one
                                                                                   # because the data has the wrong sign

        entry["weight"] = [1.0 for val in data["phase"][data["vessel_names"][II]]]
        if entry["variable"] in arteries_to_skip:
            pass
        else:
            entry["weight"][0] = 0 # zero becuase the resistance isn't free
            entry["weight"][1] = 20
            entry["weight"][2] = 6
            entry["weight"][3] = 4
            entry["weight"][4] = 3
            entry["weight"][5] = 2
        entry["phase_weight"] = [5.0 for val in data["phase"][data["vessel_names"][II]]]
        entry["phase_weight"][0] = 0.0 # zeroth entry will always be zero
        entry["phase_weight"][1] = entry["phase_weight"][0]*3
        entry["phase_weight"][2] = entry["phase_weight"][1]*2
        # TODO the below sets all of the remaining phase weights after start_range to zero
        # for II in range(4, len(entry["phase_weight"])):
        # for II in range(4, len(entry["phase_weight"])):
        #     entry["phase_weight"][II] = 0.0
        entry_list.append(entry)

        # get MPA input resistance to calc mean pressure
        if entry["variable"] == "MPA_A":
            MPA_resistance = entry["value"][0]
            MPA_mean_pressure = MPA_resistance*mean_flow

    # add entries for MPA pressure
    # I think this makes sure the model converges quickly. Not super sure
    entry = {}
    entry["variable"] = "MPA_A/u"
    entry["data_type"] = "constant"
    entry["unit"] = "J/m3" # data["impedance"]["unit"]
    entry["obs_type"] = "mean"
    entry["value"] = MPA_mean_pressure
    entry["std"] = 0.1*MPA_mean_pressure
    entry["weight"] = 0.1
    entry_list.append(entry)
    
    # entry = {}
    # entry["variable"] = "MPA_A/u"
    # entry["data_type"] = "constant"
    # entry["unit"] = "J/m3" # data["impedance"]["unit"]
    # entry["obs_type"] = "max"
    # entry["value"] = 7448
    # entry["std"] = 744.8
    # entry["weight"] = 0.1
    # entry_list.append(entry)
    
    # entry = {}
    # entry["variable"] = "MPA_A/u"
    # entry["data_type"] = "constant"
    # entry["unit"] = "J/m3" # data["impedance"]["unit"]
    # entry["obs_type"] = "min"
    # entry["value"] = 2660
    # entry["std"] = 266.0
    # entry["weight"] = 0.1
    # entry_list.append(entry)
    
    # add an entry for the frequency of the first pole
    # TODO get this from the impedance values above
    for terminal_name in terminals:

        entry = {}
        entry["variable"] = f"{terminal_name} pole frequency 1"
        entry["data_type"] = "constant"
        entry["operation"] = "RICRI_get_pole_freq_1_Hz"
        entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
        entry["unit"] = "Hz" # data["impedance"]["unit"]
        entry["obs_type"] = "constant"
        entry["value"] = 1.0
        entry["std"] = 0.1
        entry["weight"] = 0.0
        entry_list.append(entry)
        
        entry = {}
        entry["variable"] = f"{terminal_name} pole frequency 2"
        entry["data_type"] = "constant"
        entry["operation"] = "RICRI_get_pole_freq_2_Hz"
        entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
        entry["unit"] = "Hz" # data["impedance"]["unit"]
        entry["obs_type"] = "constant"
        entry["value"] = 1.0
        entry["std"] = 0.1
        entry["weight"] = 3
        entry_list.append(entry)

        entry = {}
        entry["variable"] = f"{terminal_name} zero frequency 1"
        entry["data_type"] = "constant"
        entry["operation"] = "RICRI_get_zero_freq_1_Hz"
        entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
        entry["unit"] = "Hz" # data["impedance"]["unit"]
        entry["obs_type"] = "constant"
        entry["value"] = 0.4
        entry["std"] = 0.04 
        entry["weight"] = 1.0
        entry_list.append(entry)

        entry = {}
        entry["variable"] = f"{terminal_name} zero frequency 2"
        entry["data_type"] = "constant"
        entry["operation"] = "RICRI_get_zero_freq_2_Hz"
        entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
        entry["unit"] = "Hz" # data["impedance"]["unit"]
        entry["obs_type"] = "constant"
        entry["value"] = 5.0
        entry["std"] = 0.5
        entry["weight"] = 1
        entry_list.append(entry)

        entry = {}
        entry["variable"] = f"{terminal_name} zero frequency 3"
        entry["data_type"] = "constant"
        entry["operation"] = "RICRI_get_zero_freq_3_Hz"
        entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
        entry["unit"] = "Hz" # data["impedance"]["unit"]
        entry["obs_type"] = "constant"
        entry["value"] = 5.0
        entry["std"] = 0.5
        entry["weight"] = 1
        entry_list.append(entry)

    # add an entry for total stressed volume of terminals
    entry = {}
    entry["variable"] = "stressed_volume_sum"
    entry["data_type"] = "constant"
    entry["operation"] = "addition"
    entry["operands"] = ["LUL/q_T", "RUL/q_T", "LLL/q_T", "RLL/q_T", "RML/q_T"] 
    entry["unit"] = "Js/m^6" # data["impedance"]["unit"]
    entry["obs_type"] = "mean"
    entry["value"] = 0.0001
    entry["std"] = 0.00001
    entry["weight"] = 0.001
    # TODO currently don't include the stressed volume cost
    # entry_list.append(entry)


    full_dict["data_item"] = entry_list 

    with open(save_file_path, 'w') as wf: 
        json.dump(full_dict, wf, indent=2)

    with open(constants_save_file_path, 'w') as wf:
        json.dump(constant_list, wf)

if __name__ == "__main__":

    if len(sys.argv) == 4:
        patient_num=sys.argv[1]
        pre_or_post = sys.argv[2]
        project_dir = sys.argv[3]
        if pre_or_post not in ['pre', 'post']:
            print(f'pre_or_post must be "pre" or "post", not {pre_or_post}')
            exit()
        
    else:
        print("usage:  python lungsim_impedance_to_gt_output.py patient_num pre_or_post project_dir") 
        exit()

    convert_lungsim_output_to_obs_data_json(patient_num, pre_or_post, project_dir)



