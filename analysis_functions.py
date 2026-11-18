import pandas as pd

# Analysis functions


def perc_diff_calc(flow_cols, bl_data, nf_data, ff_data, metric=None):
    # calculate percentage change from baseline to near future and baseline to far future
    bl_nf_perc = nf_data.copy()
    bl_nf_perc.loc[:,flow_cols]=100*(nf_data[flow_cols]-bl_data[flow_cols])/bl_data[flow_cols]
    
    bl_ff_perc = nf_data.copy()
    bl_ff_perc.loc[:,flow_cols]=100*(ff_data[flow_cols]-bl_data[flow_cols])/bl_data[flow_cols]
    
    # find percentiles of RCMs for each percentage change and append into single dataframe
    formatted_nf = bl_nf_perc[flow_cols].quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_nf.columns = ['10th_perc_near_fut', '50th_perc_near_fut', '90th_perc_near_fut']
    if metric=='quantiles':
        formatted_nf = bl_nf_perc[['quantile']].join(formatted_nf)
    
    formatted_ff = bl_ff_perc[flow_cols].quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_ff.columns = ['10th_perc_far_fut', '50th_perc_far_fut', '90th_perc_far_fut']
    formatted_out = formatted_nf.join(formatted_ff)
    
    return(formatted_out)
    


def perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data, metric=None):
    # calculate percentage change from baseline to near future and baseline to far future
    bl_nf_perc = nf_data.copy()
    bl_nf_perc.loc[:,flow_cols]=100*(nf_data[flow_cols]-bl_data[flow_cols])/bl_data[flow_cols]
    
    bl_ff_perc = nf_data.copy()
    bl_ff_perc.loc[:,flow_cols]=100*(ff_data[flow_cols]-bl_data[flow_cols])/bl_data[flow_cols]
    
    # find percentiles of RCMs for each percentage change and append into single dataframe
    formatted_nf = bl_nf_perc[flow_cols]
    formatted_nf.columns = [x+'_near_fut' for x in flow_cols]
    if metric=='quantiles':
        formatted_nf = bl_nf_perc[['quantile']].join(formatted_nf)
    
    formatted_ff = bl_ff_perc[flow_cols]
    formatted_ff.columns = [x+'_far_fut' for x in flow_cols]
    formatted_out = formatted_nf.join(formatted_ff)
    
    return(formatted_out)



def format_quantiles(station, flow_cols, out_dir, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    # read in quantile data
    df = pd.read_csv(out_dir+'quantiles/quantiles_30yr_window_'+station+'.csv')
    # lower the year by 29 so that it matches the start year of the window
    df.loc[:,'year'] -= 29 
    
    # extract data for the time slices
    bl_data = df.loc[df['year']==bl_start].reset_index(drop=True)
    nf_data = df.loc[df['year']==nf_start].reset_index(drop=True)
    ff_data = df.loc[df['year']==ff_start].reset_index(drop=True)
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data, metric='quantiles')
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data, metric='quantiles')
    
    return formatted_out, formatted_out_rcm


def format_annual_means(station, flow_cols, out_dir, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    # read in data
    df = pd.read_csv(out_dir+'means/annual/annual_mean_'+station+'.csv')
    
    bl_data = df.loc[(df['year']>=bl_start) & (df['year']<bl_start+30)]
    bl_data = pd.DataFrame(bl_data[flow_cols].mean()).transpose()
    
    nf_data = df.loc[(df['year']>=nf_start) & (df['year']<nf_start+30)]
    nf_data = pd.DataFrame(nf_data[flow_cols].mean()).transpose()
    
    ff_data = df.loc[(df['year']>=ff_start) & (df['year']<ff_start+30)]
    ff_data = pd.DataFrame(ff_data[flow_cols].mean()).transpose()
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm



def format_monthly_means(station, flow_cols, out_dir, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    # read in data
    df = pd.read_csv(out_dir+'means/monthly/monthly_mean_'+station+'.csv')
    
    bl_data = df.loc[(df['year']>=bl_start) & (df['year']<bl_start+30)]
    bl_data = pd.DataFrame(bl_data.groupby('month')[flow_cols].mean())
        
    nf_data = df.loc[(df['year']>=nf_start) & (df['year']<nf_start+30)]
    nf_data = pd.DataFrame(nf_data.groupby('month')[flow_cols].mean())
        
    ff_data = df.loc[(df['year']>=ff_start) & (df['year']<ff_start+30)]
    ff_data = pd.DataFrame(ff_data.groupby('month')[flow_cols].mean())
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm


def format_seasonal_means(station, flow_cols, out_dir, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    # read in data
    df = pd.read_csv(out_dir+'means/seasonal/seasonal_mean_fixed_seasons_'+station+'.csv')
    
    bl_data = df.loc[(df['year']>=bl_start) & (df['year']<bl_start+30)]
    bl_data = pd.DataFrame(bl_data.groupby('season')[flow_cols].mean())
        
    nf_data = df.loc[(df['year']>=nf_start) & (df['year']<nf_start+30)]
    nf_data = pd.DataFrame(nf_data.groupby('season')[flow_cols].mean())
        
    ff_data = df.loc[(df['year']>=ff_start) & (df['year']<ff_start+30)]
    ff_data = pd.DataFrame(ff_data.groupby('season')[flow_cols].mean())
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm


def format_extreme_flow_days(station, flow_cols, out_dir, direction, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    if direction == 'high':
        df = pd.read_csv(out_dir+'high_flow_days/high_flow_days_q5_30yr_window_'+station+'.csv')
    elif direction == 'low':
        df = pd.read_csv(out_dir+'low_flow_days/low_flow_days_q95_30yr_window_'+station+'.csv')
    else:
        raise Exception("direction not recognised, must be 'high' or 'low'")
    
    for c in flow_cols:
        df[c] = df[c].astype('float64')
    
    bl_data = df.loc[df['year']==bl_start].reset_index(drop=True)  
    nf_data = df.loc[df['year']==nf_start].reset_index(drop=True)
    ff_data = df.loc[df['year']==ff_start].reset_index(drop=True)
    
    
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm


def format_max_min_flow_days(station, flow_cols, out_dir, direction, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    if direction == 'high':
        df = pd.read_csv(out_dir+'high_flow_days/high_flow_days_max_30yr_window_'+station+'.csv')
    elif direction == 'low':
        df = pd.read_csv(out_dir+'low_flow_days/low_flow_days_min_30yr_window_'+station+'.csv')
    else:
        raise Exception("direction not recognised, must be 'high' or 'low'")
    
    for c in flow_cols:
        df[c] = df[c].astype('float64')
    
    bl_data = df.loc[df['year']==bl_start].reset_index(drop=True)  
    nf_data = df.loc[df['year']==nf_start].reset_index(drop=True)
    ff_data = df.loc[df['year']==ff_start].reset_index(drop=True)
    
    bl_nf_perc = nf_data - bl_data
    bl_ff_perc = ff_data - bl_data

    formatted_nf = bl_nf_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_nf.columns = ['10th_perc_near_fut', '50th_perc_near_fut', '90th_perc_near_fut']
        
    formatted_ff = bl_ff_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_ff.columns = ['10th_perc_far_fut', '50th_perc_far_fut', '90th_perc_far_fut']
    
    formatted_out = formatted_nf.join(formatted_ff)
    
    
    formatted_nf_rcm = bl_nf_perc[flow_cols]
    formatted_nf_rcm.columns = [x+'_near_fut' for x in flow_cols]
    
    formatted_ff_rcm = bl_ff_perc[flow_cols]
    formatted_ff_rcm.columns = [x+'_far_fut' for x in flow_cols]
    
    formatted_out_rcm = formatted_nf_rcm.join(formatted_ff_rcm)
    
    
    return formatted_out, formatted_out_rcm


def format_extreme_flow_events(station, flow_cols, out_dir, direction, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    if direction == 'high':
        df = pd.read_csv(out_dir+'high_flow_events/high_flow_events_q5_'+station+'.csv')
        col4 = 'Maximum Magnitude'
    elif direction == 'low':
        df = pd.read_csv(out_dir+'low_flow_events/low_flow_events_q95_'+station+'.csv')
        col4 = 'Minimum Magnitude'
    else:
        raise Exception("direction not recognised, must be 'high' or 'low'")
    
    bl_data = df.loc[(df['Start Year']>=bl_start)& (df['Start Year']<bl_start+30)].reset_index(drop=True)
    nf_data = df.loc[(df['Start Year']>=nf_start)& (df['Start Year']<nf_start+30)].reset_index(drop=True)
    ff_data = df.loc[(df['Start Year']>=ff_start)& (df['Start Year']<ff_start+30)].reset_index(drop=True)

    bl_data = bl_data[['flowcol', 'Duration (days)', 'Mean Magnitude', col4]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    nf_data = nf_data[['flowcol', 'Duration (days)', 'Mean Magnitude', col4]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    ff_data = ff_data[['flowcol', 'Duration (days)', 'Mean Magnitude', col4]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm


def format_extreme_flow_timing(station, flow_cols, out_dir, direction, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    if direction == 'max_wy':
        df = pd.read_csv(out_dir+'annual_max/timing_of_annual_max_water_year_'+station+'.csv')
    elif direction == 'max':
        df = pd.read_csv(out_dir+'annual_max/timing_of_annual_max_'+station+'.csv')
    elif direction == 'min':
        df = pd.read_csv(out_dir+'annual_min/timing_of_annual_min_'+station+'.csv')
    elif direction == 'min_wy':
        df = pd.read_csv(out_dir+'annual_min/timing_of_annual_min_water_year_'+station+'.csv')
    else:
        raise Exception("direction not recognised, must be 'max', 'max_wy, 'min', or 'min_wy")
        
        
    bl_data = df.loc[(df['year']>=bl_start)& (df['year']<bl_start+30)].reset_index(drop=True)
    nf_data = df.loc[(df['year']>=nf_start)& (df['year']<nf_start+30)].reset_index(drop=True)
    ff_data = df.loc[(df['year']>=ff_start)& (df['year']<ff_start+30)].reset_index(drop=True)

    bl_data = pd.DataFrame(bl_data[flow_cols].median()).transpose()
    nf_data = pd.DataFrame(nf_data[flow_cols].median()).transpose()
    ff_data = pd.DataFrame(ff_data[flow_cols].median()).transpose()

    #bl_nf_perc = 100*(nf_data - bl_data)/bl_data
    #bl_ff_perc = 100*(ff_data - bl_data)/bl_data

    bl_nf_perc = nf_data - bl_data
    bl_ff_perc = ff_data - bl_data

    formatted_nf = bl_nf_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_nf.columns = ['10th_perc_near_fut', '50th_perc_near_fut', '90th_perc_near_fut']
        
    formatted_ff = bl_ff_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_ff.columns = ['10th_perc_far_fut', '50th_perc_far_fut', '90th_perc_far_fut']
    
    formatted_out = formatted_nf.join(formatted_ff)
    
    
    formatted_nf_rcm = bl_nf_perc[flow_cols]
    formatted_nf_rcm.columns = [x+'_near_fut' for x in flow_cols]
    
    formatted_ff_rcm = bl_ff_perc[flow_cols]
    formatted_ff_rcm.columns = [x+'_far_fut' for x in flow_cols]
    
    formatted_out_rcm = formatted_nf_rcm.join(formatted_ff_rcm)
    
    
    return formatted_out, formatted_out_rcm



def format_transitions(station, flow_cols, out_dir, upperq, day_thresh=90, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    # read in data
    df = pd.read_csv(out_dir+'transition_events/Q95_to_'+upperq+'_transitions_'+station+'.csv')
    df = df.loc[df['Transition Duration'] <= day_thresh]

    raw_bl_data = df.loc[(df['Start Year']>=bl_start)& (df['Start Year']<bl_start+30)].reset_index(drop=True)
    raw_nf_data = df.loc[(df['Start Year']>=nf_start)& (df['Start Year']<nf_start+30)].reset_index(drop=True)
    raw_ff_data = df.loc[(df['Start Year']>=ff_start)& (df['Start Year']<ff_start+30)].reset_index(drop=True)

    bl_data = raw_bl_data[['flowcol', 'Transition Duration', 'Transition Magnitude']].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    nf_data = raw_nf_data[['flowcol', 'Transition Duration', 'Transition Magnitude']].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    ff_data = raw_ff_data[['flowcol', 'Transition Duration', 'Transition Magnitude']].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)

    bl_data.loc['Transition Count'] = raw_bl_data.groupby('flowcol').size()
    nf_data.loc['Transition Count'] = raw_nf_data.groupby('flowcol').size()
    ff_data.loc['Transition Count'] = raw_ff_data.groupby('flowcol').size()
    
    
    formatted_out = perc_diff_calc(flow_cols, bl_data, nf_data, ff_data)
    formatted_out_rcm = perc_diff_keep_rcm(flow_cols, bl_data, nf_data, ff_data)
    
    return formatted_out, formatted_out_rcm
    

def format_nday(station, flow_cols, out_dir, direction, n, bl_start = 1991, nf_start = 2021, ff_start = 2051):
    
    if direction == 'max':
        # read in data
        df = pd.read_csv(out_dir+'nday_max/max_'+str(n)+'_day_flows_'+station+'.csv') 
        col2 = 'Max Flow'
    elif direction == 'min':
        df = pd.read_csv(out_dir+'nday_min/min_'+str(n)+'_day_flows_'+station+'_water_year.csv')
        col2 = 'Min Flow'
    
    

    df['wy_month'] = (df['Start Month']-10)%12 +1
    df['day_of_year'] = ((df['wy_month']-1)*30)+df['Start Day']

    raw_bl_data = df.loc[(df['Start Year']>=bl_start)& (df['Start Year']<bl_start+30)].reset_index(drop=True)
    raw_nf_data = df.loc[(df['Start Year']>=nf_start)& (df['Start Year']<nf_start+30)].reset_index(drop=True)
    raw_ff_data = df.loc[(df['Start Year']>=ff_start)& (df['Start Year']<ff_start+30)].reset_index(drop=True)

    bl_data = raw_bl_data[['flowcol', col2]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    nf_data = raw_nf_data[['flowcol', col2]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)
    ff_data = raw_ff_data[['flowcol', col2]].groupby('flowcol').mean().transpose().reindex(columns=flow_cols)

    bl_data.loc['timing'] = raw_bl_data[['flowcol', 'day_of_year']].groupby('flowcol')['day_of_year'].median()
    nf_data.loc['timing'] = raw_nf_data[['flowcol', 'day_of_year']].groupby('flowcol')['day_of_year'].median()
    ff_data.loc['timing'] = raw_ff_data[['flowcol', 'day_of_year']].groupby('flowcol')['day_of_year'].median()



    bl_nf_perc = 100*(nf_data - bl_data)/bl_data
    bl_nf_perc.loc['timing'] = nf_data.loc['timing'] - bl_data.loc['timing']

    bl_ff_perc = 100*(ff_data - bl_data)/bl_data
    bl_ff_perc.loc['timing'] = ff_data.loc['timing'] - bl_data.loc['timing']


    formatted_nf = bl_nf_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_nf.columns = ['10th_perc_near_fut', '50th_perc_near_fut', '90th_perc_near_fut']
        
    formatted_ff = bl_ff_perc.quantile(q=[0.1,0.5,0.9], axis=1).transpose()
    formatted_ff.columns = ['10th_perc_far_fut', '50th_perc_far_fut', '90th_perc_far_fut']
        
    formatted_out = formatted_nf.join(formatted_ff)
    
    
    formatted_nf_rcm = bl_nf_perc[flow_cols]
    formatted_nf_rcm.columns = [x+'_near_fut' for x in flow_cols]
    
    formatted_ff_rcm = bl_ff_perc[flow_cols]
    formatted_ff_rcm.columns = [x+'_far_fut' for x in flow_cols]
    
    formatted_out_rcm = formatted_nf_rcm.join(formatted_ff_rcm)
    
    
    return formatted_out, formatted_out_rcm