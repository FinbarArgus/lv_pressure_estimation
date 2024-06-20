import json
import pandas as pd
import sys
import os

def convert_lungsim_output_to_obs_data_json(patient_num, pre_or_post, project_dir, use_CO_from_SV):

    data_file_path = os.path.join(project_dir, f'data/pulmonary/lobe_impedances/{patient_num}/{pre_or_post}/lobe_imped.json')
    vessel_array_path = os.path.join(project_dir, f"physiology_models/pulmonary_CVS_Alfred/patient_{patient_num}/{pre_or_post}/resources/lung_ROM_vessel_array.csv")
    save_file_path = os.path.join(project_dir, f'data/pulmonary/ground_truth_for_CA/ROM_gt/lung_ROM_lobe_imped_{pre_or_post}_patient_{patient_num}_obs_data.json')
    constants_save_file_path = os.path.join(project_dir, f'data/pulmonary/ground_truth_for_CA/ROM_gt/vessel_geom_constants_{pre_or_post}_patient_{patient_num}.json')

    with open(data_file_path, 'r') as file:
        data = json.load(file)

    vessel_array = pd.read_csv(vessel_array_path, index_col=0)
    # dyne_s_per_cm5_to_J_s_per_m6 
    conversion = 1e5
    l_per_min_to_ml_per_m3 = 1e-3/60
    mmHg_to_Pa = 133.32

    P_pcwp_mean = 12*mmHg_to_Pa # TODO get this from the ALL_DATA file
    MPA_mean_pressure = 33* mmHg_to_Pa # TODO this should work, currently 
                                         # the data is inconsistant

    print("################## IMPORTANT ############")
    print("Get pressures from the ALL_DATA file")
    print("################## IMPORTANT ############")

    mu = 0.004


    full_dict = {}
    entry_list = []
    constant_list = []
    terminal_names = []
    for II in range(len(data["vessel_names"])):
        # get radius and length entries
        # TODO get strained and unstrained radii, for resistance and compliance respectively
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
        
        us_radius_entry = {}
        us_radius_entry["variable_name"] = f'r_us_{data["vessel_names"][II]}'
        us_radius_entry["units"] = 'metre'
        if data['unstrained radius']['unit'] == 'mm':
            const_conversion = 1e-3
        elif data['unstrained radius']['unit'] == 'metre':
            const_conversion = 1
        else:
            print('unit of', data['unstrained radius']['unit'], 'is not implemented') 
            exit()
        us_radius_entry["value"] = const_conversion*data['unstrained radius'][data["vessel_names"][II]][0]
        us_radius_entry["data_reference"] = 'Alfred_database'
        
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
        
        length_entry["value"] = const_conversion*data['Length'][data["vessel_names"][II]][0]
        length_entry["data_reference"] = 'Alfred_database'

        constant_list.append(radius_entry)
        constant_list.append(us_radius_entry)
        constant_list.append(length_entry)

        arteries_to_skip = ["MPA_A", "LPA_A", "RPA_A", "RBS_A"] # []
        main_arteries = ["MPA_A", "LPA_A", "RPA_A"]
        terminals = ["LLL", "LUL", "RLL", "RML", "RUL"]
        
        entry = {}
        entry["variable"] = data["vessel_names"][II]
        if entry["variable"].endswith("_V"):
            # Temporarily skip the venous vessel data
            # TODO we should probably calculate downstream vessel resistance so we can better approx the
            #  terminal resistance
            continue
        
        if entry["variable"] not in arteries_to_skip:
            # terminals
            resistance_entry = {}
            terminal_name = data["vessel_names"][II].replace('_A', '')
            resistance_entry["variable_name"] = f'R_T_{terminal_name}'
            resistance_entry["units"] = 'Js_per_m6'
            resistance_entry["data_reference"] = 'Alfred_database'
            print(entry["variable"])
            if entry["variable"] == "LUL_A":
                # Figure out how to get LUL resistance properly. This is just an approximation
                if pre_or_post == 'pre':
                    approx_downstream_resistance_ratio = 0.1 # 0.2
                else: 
                    approx_downstream_resistance_ratio = 0.05 # 0.2
            else:
                if pre_or_post == 'pre':
                    # TODO find a better way to estimate the terminal resistance
                    approx_downstream_resistance_ratio = 0.4 # 0.5
                else:
                    approx_downstream_resistance_ratio = 0.2 # 0.5
            
            print(approx_downstream_resistance_ratio)
            resistance_entry["value"] = conversion*data["impedance"][data["vessel_names"][II]][0]*(1-approx_downstream_resistance_ratio)
            print(resistance_entry["value"])
            #         mod_val*8*mu*length_entry["value"]/(3.14159*radius_entry["value"]**4) #(1-approx_downstream_resistance_ratio)
            # TODO currently we don't add the resistance entry, we try to find the resistances.
            # constant_list.append(resistance_entry)


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
        entry["phase"] = [val for val in data["phase"][data["vessel_names"][II]]] # IMPORTANT phase is multiplied by negative one
                                                                                   # because the data has the wrong sign

        if entry["variable"] in arteries_to_skip:
            entry["weight"] = [0.5 for val in data["phase"][data["vessel_names"][II]]]
            # don't skip them anymore, add small weights, so the inertia knows to morph to fit these
            entry["weight"][0] = 4 # 
            entry["weight"][1] = 4 
            entry["weight"][2] = 2
            entry["weight"][3] = 1
        else:
            entry["weight"] = [1.0 for val in data["phase"][data["vessel_names"][II]]]
            # entry["weight"][0] = 6 # small because the total resistance isn't free
            entry["weight"][0] = 20 # big because total resistance is most important
            entry["weight"][1] = 20
            entry["weight"][2] = 10
            entry["weight"][3] = 6
            entry["weight"][4] = 4
            entry["weight"][5] = 3
            
        # give the main arteries a higher weight for their phase
        if data["vessel_names"][II] in main_arteries:
            entry["phase_weight"] = [5.0 for val in data["phase"][data["vessel_names"][II]]]
            entry["phase_weight"][0] = 0.0 # zeroth entry will always be zero
            entry["phase_weight"][1] = entry["phase_weight"][1]*3
            entry["phase_weight"][2] = entry["phase_weight"][2]*2
            # TODO the below sets all of the remaining phase weights after start_range to zero
            for KK in range(4, len(entry["phase_weight"])):
                entry["phase_weight"][KK] = 0.0
        else:
            entry["phase_weight"] = [2.0 for val in data["phase"][data["vessel_names"][II]]]
            entry["phase_weight"][0] = 0.0 # zeroth entry will always be zero
            entry["phase_weight"][1] = entry["phase_weight"][1]*5
            entry["phase_weight"][2] = entry["phase_weight"][2]*2
            # TODO the below sets all of the remaining phase weights after start_range to zero
            for KK in range(4, len(entry["phase_weight"])):
                entry["phase_weight"][KK] = 0.0

        # get the mean flow for this vessel
        if data['mean flow']['unit'] == 'mm3/s':
            flow_conversion = 1e-9
        else:
            print(f'flow unit of {data["mean flow"]["unit"]} is unknown')
            exit()
        mean_flow = data['mean flow'][data["vessel_names"][II]][0]*flow_conversion

        # add on the downstream resistance past the left atrium ( a ficticious resistance)
        # this is needed becuase in CA we just do the freq domain conversion on Pressure/flow
        entry["value"][0] = entry["value"][0] + P_pcwp_mean/mean_flow

        entry_list.append(entry)

        # create entry for fitting the mean flow
        flow_entry = {}
        flow_entry["variable"] = data["vessel_names"][II] + '/v'
        flow_entry["data_type"] = "constant"
        flow_entry["unit"] = "m3/s" # data["impedance"]["unit"]
        flow_entry["obs_type"] = "mean"
        flow_entry["value"] = mean_flow
        flow_entry["std"] = 0.1*mean_flow
        flow_entry["weight"] = 0.1
        entry_list.append(flow_entry)

        

        # if post get MPA input resistance to calc mean pressure and overwrite 
        # measured mean pressure
        if pre_or_post == 'post':
            if entry["variable"] == "MPA_A":
                MPA_resistance = entry["value"][0]
                MPA_mean_pressure = MPA_resistance*mean_flow # TODO should this be 
                                                             # The MPA mean pressure 
                                                             # from ALL_DATA

    # add entries for MPA pressure
    # I think this makes sure the model converges quickly. Not super sure
    entry = {}
    entry["variable"] = "MPA_A/u"
    entry["data_type"] = "constant"
    entry["unit"] = "J/m3" # data["impedance"]["unit"]
    entry["obs_type"] = "mean"
    entry["value"] = MPA_mean_pressure
    entry["std"] = 0.1*MPA_mean_pressure
    entry["weight"] = 3
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
    add_poles_zeros = False
    if add_poles_zeros:
        for terminal_name in terminals:

            entry = {}
            entry["variable"] = f"{terminal_name} pole frequency 1"
            entry["data_type"] = "constant"
            entry["operation"] = "RICRI_get_pole_freq_1_Hz"
            entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
            entry["unit"] = "Hz" # data["impedance"]["unit"]
            entry["obs_type"] = "constant"
            entry["value"] = 1.2
            entry["std"] = 0.12
            entry["weight"] = 0.0
            entry_list.append(entry)
            
            entry = {}
            entry["variable"] = f"{terminal_name} pole frequency 2"
            entry["data_type"] = "constant"
            entry["operation"] = "RICRI_get_pole_freq_2_Hz"
            entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
            entry["unit"] = "Hz" # data["impedance"]["unit"]
            entry["obs_type"] = "constant"
            entry["value"] = 1.2
            entry["std"] = 0.12
            entry["weight"] = 0.0# 3
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
            entry["weight"] = 0.0
            entry_list.append(entry)

            entry = {}
            entry["variable"] = f"{terminal_name} zero frequency 2"
            entry["data_type"] = "constant"
            entry["operation"] = "RICRI_get_zero_freq_2_Hz"
            entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
            entry["unit"] = "Hz" # data["impedance"]["unit"]
            entry["obs_type"] = "constant"
            if pre_or_post == 'pre':
                # TODO get these from the minima of the impedance curves
                entry["value"] = 4.5 
                entry["std"] = 0.45
                entry["weight"] = 0.0# 2
            else:
                entry["value"] = 8.0
                entry["std"] = 0.8
                entry["weight"] = 0.0# 2
            entry_list.append(entry)

            entry = {}
            entry["variable"] = f"{terminal_name} zero frequency 3"
            entry["data_type"] = "constant"
            entry["operation"] = "RICRI_get_zero_freq_3_Hz"
            entry["operands"] = [f"{terminal_name}/C_T", f"{terminal_name}/I_T_1", f"{terminal_name}/I_T_2", f"{terminal_name}/R_T", f"{terminal_name}/frac_R_T_1_of_R_T"] 
            entry["unit"] = "Hz" # data["impedance"]["unit"]
            entry["obs_type"] = "constant"
            if pre_or_post == 'pre':
                entry["value"] = 4.5
                entry["std"] = 0.45
                entry["weight"] = 0
            else:
                entry["value"] = 8.0
                entry["std"] = 0.8
                entry["weight"] = 0
            entry_list.append(entry)

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



