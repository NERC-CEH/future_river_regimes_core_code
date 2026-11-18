#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Tue Jan 13 12:46:18 2026

@author: eugmag
'''
import os
os.chdir('/path/to/code/')

import pandas as pd
import analysis_functions as af


data_dir = '/path/to/data/'
out_dir = '/path/to/outputs/'
formatted_dir = '/path/to/formatted_outputs/'


all_files = os.listdir(data_dir)

rcm_list = ['RCM01', 'RCM04', 'RCM05', 'RCM06', 'RCM07', 'RCM08',
            'RCM09', 'RCM10', 'RCM11', 'RCM12', 'RCM13', 'RCM15']
flow_cols = rcm_list

station_list = [filename.split('_')[3] for filename in all_files]


bl_start = 1991
nf_start = 2021
ff_start = 2051

# Define dictionary of tasks

tasks = {
    'quantiles': af.format_quantiles,
    'annual_mean': af.format_annual_means,
    'monthly_mean': af.format_monthly_means,
    'seasonal_mean': af.format_seasonal_means,
    
    'high_flow_days': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_days(station, flow_cols, out_dir, 'high', bl, nf, ff),
    
    'low_flow_days': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_days(station, flow_cols, out_dir, 'low', bl, nf, ff),
        
    'max_flow_days': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_max_min_flow_days(station, flow_cols, out_dir, 'high', bl, nf, ff),
    
    'min_flow_days': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_max_min_flow_days(station, flow_cols, out_dir, 'low', bl, nf, ff),
    
    'high_flow_events': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_events(station, flow_cols, out_dir, 'high', bl, nf, ff),
    
    'low_flow_events': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_events(station, flow_cols, out_dir, 'low', bl, nf, ff),
    
    'timing_of_annual_max': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_timing(station, flow_cols, out_dir, 'max', bl, nf, ff),
    
    'timing_of_annual_max_water_year': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_timing(station, flow_cols, out_dir, 'max_wy', bl, nf, ff),
    
    'timing_of_annual_min': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_timing(station, flow_cols, out_dir, 'min', bl, nf, ff),
        
    'timing_of_annual_min_water_year': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_extreme_flow_timing(station, flow_cols, out_dir, 'min_wy', bl, nf, ff),
    
    'transition_events_Q50': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_transitions(station, flow_cols, out_dir, 'Q50', 90, bl, nf, ff),
        
    'transition_events_Q5': lambda station, flow_cols, out_dir, bl, nf, ff:
        af.format_transitions(station, flow_cols, out_dir, 'Q5', 90, bl, nf, ff)
}
    

nday_modes = ["min", "max"]
nday_windows = [3, 7, 14, 30]

for mode in nday_modes:
    for n in nday_windows:
        task_name = f'{mode}_{n}_day'
        tasks[task_name] = (            
            lambda station, flow_cols, out_dir, bl, nf, ff, m=mode, nd=n:
                af.format_nday(station, flow_cols, out_dir, m, nd, bl, nf, ff)
            )


# Define dictionary of columns to drop/rename for each metric
column_handling = {
    'quantiles': {
        'drop': ['level_1'],
        'rename': {}
    },
    'annual_mean': {
        'drop': ['level_1'],
        'rename': {}
    },
    'monthly_mean': {
        'drop': [],
        'rename': {}
    },
    'seasonal_mean': {
        'drop': [],
        'rename': {}
    },
    'high_flow_days': {
        'drop': ['level_1'],
        'rename': {}
    },
    'low_flow_days': {
        'drop': ['level_1'],
        'rename': {}
    },
    'max_flow_days': {
        'drop': ['level_1'],
        'rename': {}
    },
    'min_flow_days': {
        'drop': ['level_1'],
        'rename': {}
    },
    'high_flow_events':{
        'drop':[],
        'rename':{'level_1': 'metric'}
    },
    'low_flow_events':{
        'drop':[],
        'rename':{'level_1': 'metric'}
    },
    'timing_of_annual_max':{
        'drop': ['level_1'],
        'rename': {}
    },
    'timing_of_annual_max_water_year':{
        'drop': ['level_1'],
        'rename': {}
    },
    'timing_of_annual_min':{
        'drop': ['level_1'],
        'rename': {}
    },
    'transition_events_Q50':{
        'drop':[],
        'rename':{'level_1': 'metric'}
    },
    'transition_events_Q5':{
        'drop':[],
        'rename':{'level_1': 'metric'}
    }
    
}

# Append tasks and column handling for n-day windows
for mode in nday_modes:
    for n in nday_windows:
        task_name = f'{mode}_{n}_day'
        column_handling[task_name] = {
            'drop':[],
            'rename':{'level_1': 'metric'}
            }
    

# Set up results dictionary
results = {task: {'percentiles': {}, 'all_rcm': {}} for task in tasks}


# Loop over stations and tasks
for station in station_list:
    for task_name, func in tasks.items():
        # Run the function in the task list to get the percentile and rcm dataframes
        percentiles_df, rcm_df = func(station, flow_cols, out_dir, bl_start, nf_start, ff_start)
        results[task_name]['percentiles'][station] = percentiles_df
        results[task_name]['all_rcm'][station] = rcm_df

# Define function to concatenate the dataframes to include all stations in single dataframe
def stack_by_station(dfs_by_station):
    stacked = pd.concat(dfs_by_station, names=['station']).reset_index()
    if stacked.columns[0] != 'station':
        stacked.rename(columns={stacked.columns[0]: 'station'}, inplace=True)
    return stacked

# Apply the function to get a single data frame when calling final_tables[task_name][aggr] 
final_tables = {
    task: {
        'percentiles': stack_by_station(aggr['percentiles']),
        'all_rcm': stack_by_station(aggr['all_rcm']),
    }
    for task, aggr in results.items()
}



# Loop over tasks and aggregation type
for task, aggr in final_tables.items():
    for aggr_name, df in aggr.items():
        config = column_handling.get(task, {})
        
        # Drop columns
        if 'drop' in config:
            df = df.drop(columns=[c for c in config['drop'] if c in df.columns])
        
        # Rename columns
        if 'rename' in config:
            df = df.rename(columns={k: v for k, v in config['rename'].items() if k in df.columns})
        
        # Write to csv
        df.to_csv(f'{formatted_dir}{task}_summary_{aggr_name}.csv', index=False)


