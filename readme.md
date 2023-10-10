For Preprocessing of data for circulatory_autogen

This repo has scripts and functions for working with datasets to get them in json files ready for circulatory autogen.

/user_run_scripts/get_intrabeat_periods.py inputs csv file with only ecg data and outputs the intrabeat periods. 

/user_run_scripts/write_data_to_csv.py writes tomtex and invasive (including ecg) data to csv for use in get_valve_data.py

/user_run_scripts/get_valve_data.py inputs the csv or pickle files generated from tomtec and invasive biobeat data and turns them into ground truth variable and constant json files.






