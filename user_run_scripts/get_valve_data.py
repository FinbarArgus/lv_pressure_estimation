import os, sys
root_dir_path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.append(sys.path.join(root_dir_path, 'python_ECG_tools'))
sys.path.append(sys.path.join(root_dir_path, 'ultrasound_uncertainty_tools'))
sys.path.append(sys.path.join(root_dir_path, 'circulatory_autogen'))

from haemotools.BB_echo_functions import BBdata
from read_tomtec_worksheets import read_tomtec_worksheets
ec = BBdata()
path = '/heart-eresearch/Projects/biobeat/data/pressures/invasive'
data = ec.data_dict_general(path)
import pdb; pdb.set_trace()
all_labels = ec.dict_counter(data)
print(all_labels.keys())
patients_with_LV = all_labels['LV']
patients_with_AO = all_labels['AO']
patients_with_AO_and_LV = list(set(patients_with_AO['idxs']) & set(patients_with_LV['idxs']))

tomtec_data

