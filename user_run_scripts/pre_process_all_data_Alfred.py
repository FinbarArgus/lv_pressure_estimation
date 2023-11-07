from lungsim_impedance_to_gt_outputs import convert_lungsim_output_to_obs_data_json 
from get_intrabeat_periods import generate_intrabeat_periods_json
from create_gt_Alfred import create_gt_obs_data_Alfred

if __name__ == "__main__":

    patient_nums = [4, 7]
    project_dir = '/home/farg967/Documents'
    # project_dir = '/hpc/farg967/pulmonary_workspace'

    for patient_num in patient_nums:

        convert_lungsim_output_to_obs_data_json(patient_num, "pre", project_dir)
        convert_lungsim_output_to_obs_data_json(patient_num, "post", project_dir)

        generate_intrabeat_periods_json(patient_num, project_dir)
        create_gt_obs_data_Alfred(patient_num, project_dir)
    

