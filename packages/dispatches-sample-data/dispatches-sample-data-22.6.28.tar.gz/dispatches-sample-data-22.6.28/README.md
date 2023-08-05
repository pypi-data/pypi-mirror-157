# dispatches-sample-data

Various datasets for use in examples of the [DISPATCHES project](https//github.com/gmlc-dispatches/dispatches), distributed as a Python package for ease of access.

## Datasets

- `dispatches_sample_data.rts_gmlc`: A subset of the data available at https://github.com/GridMod/RTS-GMLC

## Usage

To install the package:

```sh
pip install dispatches-sample-data
pip install git+https://github.com/gmlc-dispatches/sample-data
```

Importing and using the package in Python code:

```py
from dispatches_sample_data import rts_gmlc

print(rts_gmlc.path)  # .path is a pathlib.Path object with the absolute path to the directory containing the data

for csv_path in sorted(rts_gmlc.path.rglob("*.csv")):
    print(csv_path)
```

## Inspecting the installed datasets

After installing, you might want to verify that all the expected files are present. 

Using the `rts_gmlc` dataset as an example, run the following command to list all the CSV files:

```sh
python -c "from dispatches_sample_data import rts_gmlc as data; [print(p) for p in sorted(data.path.rglob('*.csv'))]"
```

The output should be something like:

```txt
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/HR_data/Final_Fits.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/HR_data/gen_oldHRs.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/branch.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/bus.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/dc_branch.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/gen.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/simulation_objects.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/storage.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/SourceData/timeseries_pointers.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/CSP/DAY_AHEAD_Natural_Inflow.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/CSP/REAL_TIME_Natural_Inflow.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Hydro/DAY_AHEAD_hydro.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Hydro/REAL_TIME_hydro.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/DAY_AHEAD_regional_Load.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/REAL_TIME_regional_Load.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/APS_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/LDWP_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/NEVP_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/RT_APS_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/RT_LDWP_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Load/origin/RT_NEVP_Promod_2020.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/PV/DAY_AHEAD_pv.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/PV/REAL_TIME_pv.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/RTPV/DAY_AHEAD_rtpv.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/RTPV/REAL_TIME_rtpv.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Flex_Down.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Flex_Up.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Reg_Down.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Reg_Up.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Spin_Up_R1.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Spin_Up_R2.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/DAY_AHEAD_regional_Spin_Up_R3.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/REAL_TIME_regional_Reg_Down.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/REAL_TIME_regional_Reg_Up.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/REAL_TIME_regional_Spin_Up_R1.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/REAL_TIME_regional_Spin_Up_R2.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/Reserves/REAL_TIME_regional_Spin_Up_R3.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/WIND/DAY_AHEAD_wind.csv
/opt/conda/envs/test-dispatches-sd/lib/python3.7/site-packages/dispatches_sample_data/rts_gmlc/timeseries_data_files/WIND/REAL_TIME_wind.csv
```
