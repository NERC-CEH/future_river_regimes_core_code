import os
import pandas as pd
import numpy as np
from tqdm import tqdm

os.chdir('/path/to/code/')

import metric_functions as met

data_dir = '/path/to/data/'

out_dir = '/path/to/outputs/'



all_files = os.listdir(data_dir)

rcm_list = ['RCM01', 'RCM04', 'RCM05', 'RCM06', 'RCM07', 'RCM08',
            'RCM09', 'RCM10', 'RCM11', 'RCM12', 'RCM13', 'RCM15']


for i in tqdm(range(len(all_files))):
    
    filename = all_files[i]
    station_name = filename.split('_')[3]
    
    flow_data = pd.read_csv(data_dir+filename, skiprows=45, skipfooter=1, index_col=0, engine='python')
    flow_data.columns = rcm_list


    # add date columns to a second datafrae
    idx = flow_data.index.to_series()

    flow_data_with_date = flow_data.copy()
    flow_data_with_date['year'] = idx.str[:4]
    flow_data_with_date['month'] = idx.str[5:7]
    flow_data_with_date['day'] = idx.str[8:10]

    for col in ['year', 'month', 'day']:
        flow_data_with_date[col] = pd.to_numeric(flow_data_with_date[col]).astype(int)

    for col in rcm_list:
        flow_data_with_date[col] = pd.to_numeric(flow_data_with_date[col]).astype(float)
        
    
    
    # Flow Duration Curve data
    fdc = met.flow_duration_curve(flow_data_with_date, flow_cols=rcm_list)
    fdc.to_csv(f'{out_dir}fdc/all/flow_duration_curve_{station_name}.csv')
    
    fdc = met.flow_duration_curve(flow_data_with_date, flow_cols=rcm_list, window_start=1991, window_end=2020)
    fdc.to_csv(f'{out_dir}fdc/1991-2020/flow_duration_curve_1991-2020_{station_name}.csv')
    
    fdc = met.flow_duration_curve(flow_data_with_date, flow_cols=rcm_list, window_start=2021, window_end=2050)
    fdc.to_csv(f'{out_dir}fdc/2021-2050/flow_duration_curve_2021-2050_{station_name}.csv')
    
    fdc = met.flow_duration_curve(flow_data_with_date, flow_cols=rcm_list, window_start=2051, window_end=2080)
    fdc.to_csv(f'{out_dir}fdc/2051-2080/flow_duration_curve_2051-2080_{station_name}.csv')

    
    # Flow Quantile data
    flow_qs = [99,95,90,50,10,5,1]
    #q = met.flow_quantiles(flow_data, flow_qs)
    q2 = met.flow_quantiles_window(flow_data_with_date, flow_cols=rcm_list, quantiles=flow_qs)
    
    q2.to_csv(f'{out_dir}quantiles/quantiles_30yr_window_{station_name}.csv')
    
    
    # Number of low-flow days data
    low_flow_days = met.count_low_flow_days(flow_data_with_date, flow_cols=rcm_list)
    low_flow_days.to_csv(f'{out_dir}low_flow_days/low_flow_days_q95_30yr_window_{station_name}.csv')
    
    low_flow_days = met.count_low_flow_days(flow_data_with_date, flow_cols=rcm_list, quantile=100) #Q100 is minimum flow
    low_flow_days.to_csv(f'{out_dir}low_flow_days/low_flow_days_min_30yr_window_{station_name}.csv')
    
    # Low-flow event detection
    low_flow_events = met.threshold_events(flow_data_with_date, flow_cols=rcm_list, quantile=95, direction='below')
    low_flow_events.to_csv(f'{out_dir}low_flow_events/low_flow_events_q95_{station_name}.csv', index=False)
    
    low_flow_events = met.threshold_events(flow_data_with_date, flow_cols=rcm_list, quantile=100, direction='below')
    low_flow_events.to_csv(f'{out_dir}low_flow_events/low_flow_events_min_{station_name}.csv', index=False)
    
    
    # Number of high-flow days data
    high_flow_days = met.count_high_flow_days(flow_data_with_date, flow_cols=rcm_list)
    high_flow_days.to_csv(f'{out_dir}high_flow_days/high_flow_days_q5_30yr_window_{station_name}.csv')

    high_flow_days = met.count_high_flow_days(flow_data_with_date, flow_cols=rcm_list, quantile=0) #Q0 is maximum flow
    high_flow_days.to_csv(f'{out_dir}high_flow_days/high_flow_days_max_30yr_window_{station_name}.csv')
    
    # High-flow event detection
    high_flow_events = met.threshold_events(flow_data_with_date, flow_cols=rcm_list, quantile=5, direction='above')
    high_flow_events.to_csv(f'{out_dir}high_flow_events/high_flow_events_q5_{station_name}.csv', index=False)
    
    high_flow_events = met.threshold_events(flow_data_with_date, flow_cols=rcm_list, quantile=0, direction='above')
    high_flow_events.to_csv(f'{out_dir}high_flow_events/high_flow_events_max_{station_name}.csv', index=False)
    
    
    # Timing of annual extremes
    annual_max_data = met.annual_extreme_timing(flow_data_with_date, flow_cols=rcm_list, direction='max', wy=False)
    annual_max_data.to_csv(f'{out_dir}annual_max/timing_of_annual_max_{station_name}.csv')
    
    annual_max_data = met.annual_extreme_timing(flow_data_with_date, flow_cols=rcm_list, direction='max', wy=True)
    annual_max_data.to_csv(f'{out_dir}annual_max/timing_of_annual_max_water_year_{station_name}.csv')
    
    annual_min_data = met.annual_extreme_timing(flow_data_with_date, flow_cols=rcm_list, direction='min', wy=False)
    annual_min_data.to_csv(f'{out_dir}annual_min/timing_of_annual_min_{station_name}.csv')
    
    annual_min_data = met.annual_extreme_timing(flow_data_with_date, flow_cols=rcm_list, direction='min', wy=True)
    annual_min_data.to_csv(f'{out_dir}annual_min/timing_of_annual_min_water_year_{station_name}.csv')
    
    
    
    # Means
    annual_mean_data = met.annual_mean(flow_data_with_date, flow_cols=rcm_list)
    annual_mean_data.to_csv(f'{out_dir}means/annual/annual_mean_{station_name}.csv')
    
    seasonal_mean_data = met.seasonal_mean(flow_data_with_date, flow_cols=rcm_list)
    seasonal_mean_data.to_csv(f'{out_dir}means/seasonal/seasonal_mean_fixed_seasons_{station_name}.csv')
    
    seasonal_mean_data = met.seasonal_mean(flow_data_with_date, flow_cols=rcm_list, fix_seasons=False)
    seasonal_mean_data.to_csv(f'{out_dir}means/seasonal/seasonal_mean_{station_name}.csv')
    
    monthly_mean_data = met.monthly_mean(flow_data_with_date, flow_cols=rcm_list)
    monthly_mean_data.to_csv(f'{out_dir}means/monthly/monthly_mean_{station_name}.csv')


    # Get long term mean data for plott "mean hydrographs"
    long_term_mean_data = met.long_term_mean(flow_data_with_date, flow_cols=rcm_list)
    long_term_mean_data.to_csv(f'{out_dir}means/long_term_daily/all/long_term_mean_{station_name}.csv')
    
    long_term_mean_data = met.long_term_mean(flow_data_with_date, flow_cols=rcm_list, window_start=1991, window_end=2020)
    long_term_mean_data.to_csv(f'{out_dir}means/long_term_daily/1991-2020/long_term_mean_1991-2020_{station_name}.csv')
    
    long_term_mean_data = met.long_term_mean(flow_data_with_date, flow_cols=rcm_list, window_start=2021, window_end=2050)
    long_term_mean_data.to_csv(f'{out_dir}means/long_term_daily/2021-2050/long_term_mean_2021-2050_{station_name}.csv')
    
    long_term_mean_data = met.long_term_mean(flow_data_with_date, flow_cols=rcm_list, window_start=2051, window_end=2080)
    long_term_mean_data.to_csv(f'{out_dir}means/long_term_daily/2051-2080/long_term_mean_2051-2080_{station_name}.csv')


    n_day_list = [3,7,14,30]
    for n in n_day_list:
        min_day = met.nday_flows(flow_data_with_date, flow_cols=rcm_list, n=n, direction='min', wy=True)
        min_day.to_csv(f'{out_dir}nday_min/min_{str(n)}_day_flows_{station_name}_water_year.csv', index=False)
        
        max_day = met.nday_flows(flow_data_with_date, flow_cols=rcm_list, n=n, direction='max', wy=True)
        max_day.to_csv(f'{out_dir}nday_max/max_{str(n)}_day_flows_{station_name}_water_year.csv', index=False)
        
        max_day = met.nday_flows(flow_data_with_date, flow_cols=rcm_list, n=n, direction='max', wy=False)
        max_day.to_csv(f'{out_dir}nday_max/max_{str(n)}_day_flows_{station_name}.csv', index=False)
    
    transition_events = met.transition_event_extraction(flow_data_with_date, flow_cols=rcm_list, upper_quant=5, lower_quant=95)
    transition_events.to_csv(f'{out_dir}transition_events/Q95_to_Q5_transitions_{station_name}.csv', index=False)
    
    transition_events = met.transition_event_extraction(flow_data_with_date, flow_cols=rcm_list, upper_quant=50, lower_quant=95)
    transition_events.to_csv(f'{out_dir}transition_events/Q95_to_Q50_transitions_{station_name}.csv', index=False)