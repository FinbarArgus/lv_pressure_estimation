from lungsim_impedance_to_gt_outputs import convert_lungsim_output_to_obs_data_json 
from get_intrabeat_periods import generate_intrabeat_periods_json
from create_gt_Alfred import create_gt_obs_data_Alfred

if __name__ == "__main__":

    patient_nums = [4, 7]

    for patient_num in patient_nums:

        convert_lungsim_output_to_obs_data_json(patient_num, "pre")
        convert_lungsim_output_to_obs_data_json(patient_num, "post")

        generate_intrabeat_periods_json(patient_num)
        create_gt_obs_data_Alfred(patient_num)
    

