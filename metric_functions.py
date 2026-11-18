"""
IMPORTANT

All the functions here assume you have a dataframe with one or more columns containing daily flow values
The flow columns can have any name and are defined when you call the functions.
There is also the assumption that there are three columns to represent the date: year, month, day.
They were originally written to work with data derived from UKCP18 projections with 360 day years meaning datetime manipulation would break.
All functions will also work with standard dates, provided the three required columns are present.

"""

import pandas as pd
import numpy as np


def flow_quantiles_window(df, flow_cols, quantiles=[90], window=30):
    '''
    
    Function to calculate flow quantiles for transient moving windows.
    Setting window to 1 will give annual quantiles, otherwise the quantiles are calculated from all data in the window.
    Default window width of 30 years.
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    quantiles : list, optional
        list of flow quantiles to calculate, eg the default of [90] will calculate Q90 values. The default is [90].
    window : integer, optional
        width of window, in years, over which rolling quantiles will be calculated. The default is 30.

    Returns
    -------
    result : pandas dataframe
        Dataframe of quantiles for each window and flow column.

    '''
    
    
    # Get unique sorted years
    all_years = sorted(df['year'].dropna().unique())

    results = []
    
    pvals = [(100 - q) / 100 for q in quantiles]

    for year in all_years[window - 1:]:
        start_year = year - window + 1
        window_df = df[(df['year'] >= start_year) & (df['year'] <= year)]

        # Compute quantiles for this window
        qdf = window_df[flow_cols].quantile(pvals)
        qdf.index = quantiles
        qdf['year'] = year

        results.append(qdf)


    result = pd.concat(results).set_index(['year'], append=True).reorder_levels(['year', None])
    result.index.names = ['year', 'quantile']
   
    result = result.round(3)
    
    result = result.astype({
        col: 'float32'
        for col in result.select_dtypes(include=['float64']).columns
    })
    return result




def flow_duration_curve_superseeded(df, flow_cols, window_start=None, window_end=None, length_out=None):
    '''
    
    Function for calculating values to plot as a flow duration curve.
    Returns a dataframe with flow values and corresponding exceedence probabilities.
    Plotting flow on y and exceedence on x gives a flow duration curve.
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    window_start : integer, optional
        Year for start of flow duration curve window, if None it will take the earliest year in the dataset. The default is None.
    window_end : integer, optional
        Year for end of flow duration curve window, if None it will take the latest year in the dataset. The default is None.

    Returns
    -------
    fdc_df : pandas dataframe
        ordered list of flow values and corresponding exceedence probabilities, used to plot a flow duration curve.

    '''
    # Get unique sorted years
    all_years = sorted(df['year'].dropna().unique())
    
    if window_start==None:
        window_start=all_years[0]
        
    if window_end==None:
        window_end=all_years[-1]
    
    window_df = df[(df['year'] >= window_start) & (df['year'] <= window_end)]
    
    window_df = window_df[flow_cols]
    
    sort = np.sort(window_df, axis=0)[::-1]
    
    index_vals = (np.arange(1,len(sort)+1)/len(sort) )* 100
    
    fdc_df = pd.DataFrame(sort)
    
    fdc_df.index=index_vals
    fdc_df.index.name='exceedence percent'
    
    
    fdc_df.columns=flow_cols

    if length_out:
        fdc_df = fdc_df.iloc[np.linspace(0, len(fdc_df)-1, length_out).astype(int)]
    
    return fdc_df.round(3)
    
    
def flow_duration_curve(df, flow_cols, window_start=None, window_end=None, length_out=None, n_exceedance=1001):
    '''
    
    Function for calculating values to plot as a flow duration curve.
    Returns a dataframe with flow values and corresponding exceedence probabilities.
    Plotting flow on y and exceedence on x gives a flow duration curve.
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    window_start : integer, optional
        Year for start of flow duration curve window, if None it will take the earliest year in the dataset. The default is None.
    window_end : integer, optional
        Year for end of flow duration curve window, if None it will take the latest year in the dataset. The default is None.
    length_out : integer, optional
         Number of output exceedance points after thinning. The default is None.

    Returns
    -------
    fdc_df : pandas dataframe
        ordered list of flow values and corresponding exceedence probabilities, used to plot a flow duration curve.

    '''

    all_years = sorted(df["year"].dropna().unique())

    if window_start is None:
        window_start = all_years[0]

    if window_end is None:
        window_end = all_years[-1]

    window_df = df.loc[
        (df["year"] >= window_start) &
        (df["year"] <= window_end),
        flow_cols
    ]

    # Common exceedance grid
    exceedance_grid = np.linspace(0, 100, n_exceedance)

    fdc_dict = {}

    for col in flow_cols:

        flows = window_df[col].dropna()

        if len(flows) == 0:
            fdc_dict[col] = np.full_like(exceedance_grid, np.nan, dtype=float)
            continue

        flows = np.sort(flows)[::-1]

        exceedance = (np.arange(1, len(flows) + 1)/ len(flows)) * 100

        # Add endpoints for interpolation
        exceedance = np.concatenate([[0], exceedance])
        flows = np.concatenate([[flows[0]], flows])

        fdc_dict[col] = np.interp(
            exceedance_grid,
            exceedance,
            flows
        )

    fdc_df = pd.DataFrame(fdc_dict, index=exceedance_grid)

    fdc_df.index.name = "exceedence percent"

    if length_out:
        fdc_df = fdc_df.iloc[np.linspace(0, len(fdc_df)-1, length_out).astype(int)]
    
    fdc_df = fdc_df.round(3)

    fdc_df = fdc_df.astype({
        col: 'float32'
        for col in fdc_df.select_dtypes(include=['float64']).columns
    })
    
    return fdc_df



def count_low_flow_days(df, flow_cols, window=30, quantile=95, baseline_start=1991, baseline_end=2020):
    '''
    
    Function for counting the number of days where flow is below a defined quantile.
    The threshold is calculated from a baseline period, defined by the start and end inputs. These years are inclusive.
    
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    window : integer, optional
        width of window, in years, over which rolling count of low-flow days will be calculated. The default is 30.
    percentile : numeric between 0 and 100, optional
        the flow quantile to use as threshold for low-flow days . The default is 95.
    baseline_start : integer, optional
        Start year of the period to use as baseline for calculating the quantile threshold. The default is 1991.
    baseline_end : integer, optional
        End year of the period to use as baseline for calculating the quantile threshold. The default is 2020.

    Returns
    -------
    out : pandas dataframe
        Count of the number of days in each window where flow is below the defined quantile. The year is the start of the window.

    '''
    
    # Prepare output
    results = []

    baseline_df = df[(df['year'] >= baseline_start) & (df['year'] <= baseline_end)]
    # Compute percentile for each RCM in the window
    percentile=(100-quantile)/100
    thresholds = baseline_df[flow_cols].quantile(percentile)

    
    all_years = sorted(df['year'].unique())
    
    
    for year in all_years[window-1:]:
        # Define moving window
        start_year = year - window + 1
        window_df = df[(df['year'] >= start_year) & (df['year'] <= year)]
        
        
        if len(window_df) == 0:
            continue

        # Get days in the current window below threshold
        below = (window_df[flow_cols] < thresholds).sum()

        below['year'] = start_year
        results.append(below)
    
    # Combine into a single DataFrame
    out = pd.DataFrame(results).set_index('year')

    
    
    return out



def count_high_flow_days(df, flow_cols, window=30, quantile=5, baseline_start=1991, baseline_end=2020):
    '''
    
    Function for counting the number of days where flow is above a defined quantile.
    The threshold is calculated from a baseline period, defined by the start and end inputs. These years are inclusive.
    
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    window : integer, optional
        width of window, in years, over which rolling count of low-flow days will be calculated. The default is 30.
    percentile : numeric between 0 and 100, optional
        the flow quantile to use as threshold for high-flow days . The default is 5.
    baseline_start : integer, optional
        Start year of the period to use as baseline for calculating the quantile threshold. The default is 1991.
    baseline_end : integer, optional
        End year of the period to use as baseline for calculating the quantile threshold. The default is 2020.

    Returns
    -------
    out : pandas dataframe
        Count of the number of days in each window where flow is below the defined quantile. The year is the start of the window.

    '''
    
    # Prepare output
    results = []

    baseline_df = df[(df['year'] >= baseline_start) & (df['year'] <= baseline_end)]
    # Compute percentile for each RCM in the window
    percentile=(100-quantile)/100
    thresholds = baseline_df[flow_cols].quantile(percentile)

    
    all_years = sorted(df['year'].unique())
    
    
    for year in all_years[window-1:]:
        # Define moving window
        start_year = year - window + 1
        window_df = df[(df['year'] >= start_year) & (df['year'] <= year)]
        
        
        if len(window_df) == 0:
            continue

        # Get days in the current window below threshold
        above = (window_df[flow_cols] > thresholds).sum()

        above['year'] = start_year
        results.append(above)
    
    # Combine into a single DataFrame
    out = pd.DataFrame(results).set_index('year')
    return out




def threshold_events(df, flow_cols, quantile=95, direction='below', baseline_start=1991, baseline_end=2020):
    '''
    
    Function for extracting events where flow is above or below a defined quantile.
    The threshold is calculated from a baseline period, defined by the start and end inputs. These years are inclusive.
    
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    percentile : numeric between 0 and 100, optional
        the flow quantile to use as threshold for low-flow days . The default is 95.
    direction : str, optional
        one of "above" or "below", determines whether events above or below the given qualtile are extracted. Default is below
    baseline_start : integer, optional
        Start year of the period to use as baseline for calculating the quantile threshold. The default is 1991.
    baseline_end : integer, optional
        End year of the period to use as baseline for calculating the quantile threshold. The default is 2020.

    Returns
    -------
    out : pandas dataframe
        Dataframe of all events that meet the threshold criteria

    '''

    df = df.copy()
    
    # Prepare output
    events = []
    
    baseline_df = df[(df['year'] >= baseline_start) & (df['year'] <= baseline_end)]
    # Compute percentile for each RCM in the window
    percentile=(100-quantile)/100
    thresholds = baseline_df[flow_cols].quantile(percentile)
    
    # Create day index to force correct order
    df['day_index'] = (df['year']*360 + (df['month']-1)*30 + (df['day']-1))
    df = df.sort_values('day_index').reset_index(drop=True)
    
    for col in flow_cols:
        threshold  = thresholds[col]
        
        if direction=='below':
            event_days = df[col] < threshold
        elif direction=='above':
            event_days = df[col] > threshold
        else:
            raise Exception("Direction not recognised, must be either 'above' or 'below'")
        
        event_starts = (event_days & ~event_days.shift(fill_value=False))
        event_ends = (event_days & ~event_days.shift(-1,fill_value=False))
        
        start_ids = event_starts.index[event_starts].tolist()
        end_ids   = event_ends.index[event_ends].tolist()
        
        for s, e in zip(start_ids, end_ids):

            duration = df.loc[e, "day_index"] - df.loc[s, "day_index"] + 1

            # Extract raw data for magnitude calculations
            event_flows = df.loc[s:e, col]
            mean_mag = event_flows.mean()
            

            # Extract original year, month, and day
            start_year  = df.loc[s, "year"]
            start_month = df.loc[s, "month"]
            start_day   = df.loc[s, "day"]
            
            if direction=='below':
                min_mag = event_flows.min()
                
                events.append({
                    "Start Year": start_year,
                    "Start Month": start_month,
                    "Start Day": start_day,
                    "Duration (days)": duration,
                    "flowcol": col,
                    "Mean Magnitude": mean_mag,
                    "Minimum Magnitude": min_mag
                })
            elif direction=='above':
                max_mag = event_flows.max()
                
                events.append({
                    "Start Year": start_year,
                    "Start Month": start_month,
                    "Start Day": start_day,
                    "Duration (days)": duration,
                    "flowcol": col,
                    "Mean Magnitude": mean_mag,
                    "Maximum Magnitude": max_mag
                })
            
            
    
    # Combine into a single DataFrame
    out = pd.DataFrame(events)
    out = out.round(3)
    out = out.astype({
        col: 'float32'
        for col in out.select_dtypes(include=['float64']).columns
    })
    return out


def annual_max_timing(df, flow_cols, wy=True):
    '''
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    wy : boolean, optional
        Whether or not to use a water year (Oct-Sep), if False, calendar year (Jan-Dec) is used. Default is True

    Returns
    -------
    peak_days : pandas dataframe
        Dataframe containing year and flow columns. Values are the day of year on which annual maximum occurs.

    '''
    
    df = df.copy()
    
    is_360_day = df['day'].max() <= 30

    if wy:
        if is_360_day:
            df.loc[df['month']<=9, 'year'] -= 1
            
            df['wy_month'] = (df['month'] - 10) % 12 + 1
            df['day_of_year'] = (df['wy_month'] - 1) * 30 + df['day']
            
        else:
            date = pd.to_datetime(df[['year', 'month', 'day']])
    
            wy_start_year = np.where(
                df['month'] >= 10,
                df['year'],
                df['year'] - 1
            )
    
            wy_start = pd.to_datetime({
                'year': wy_start_year,
                'month': 10,
                'day': 1
            })
    
            df['day_of_year'] = (date - wy_start).dt.days + 1
    
    else:
    
        if is_360_day:
            df['day_of_year'] = (df['month'] - 1) * 30 + df['day']
    
        else:
            date = pd.to_datetime(df[['year', 'month', 'day']])
            df['day_of_year'] = date.dt.dayofyear


    idx = df.groupby('year')[flow_cols].idxmax()

    peak_days = pd.DataFrame({
        col: df['day_of_year'].reindex(idx[col]).to_numpy()
        for col in flow_cols
    }, index=idx.index)

    peak_days.index.name = 'year'
    
    return peak_days
    



def annual_min_timing(df, flow_cols):
    '''
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.

    Returns
    -------
    peak_days : pandas dataframe
        Dataframe containing year and flow columns. Values are the day of year on which annual minimum occurs.

    '''
    df = df.copy()
    
    df['day_of_year'] = ((df['month']-1)*30)+df['day']

    idx = df.groupby('year')[flow_cols].idxmin()

    peak_days = pd.DataFrame({
        col: df['day_of_year'].reindex(idx[col]).to_numpy()
        for col in flow_cols
    }, index=idx.index)

    peak_days.index.name = 'year'
    
    return peak_days
    


def annual_extreme_timing(df, flow_cols, direction, wy=True):
    '''
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    direction : str
        one of "max" or "min", determines which extreme to calculate.
    wy : boolean, optional
        Whether or not to use a water year (Oct-Sep) instead of the default calendar year. Default is True

    Returns
    -------
    peak_days : pandas dataframe
        Dataframe containing year and flow columns. Values are the day of year on which annual maximum occurs.

    '''
    df = df.copy()
    
    is_360_day = df['day'].max() <= 30

    if wy:
        if is_360_day:
            df.loc[df['month']<=9, 'year'] -= 1
            
            df['wy_month'] = (df['month'] - 10) % 12 + 1
            df['day_of_year'] = (df['wy_month'] - 1) * 30 + df['day']
            
        else:
            date = pd.to_datetime(df[['year', 'month', 'day']])
    
            wy_start_year = np.where(
                df['month'] >= 10,
                df['year'],
                df['year'] - 1
            )
    
            wy_start = pd.to_datetime({
                'year': wy_start_year,
                'month': 10,
                'day': 1
            })
    
            df['day_of_year'] = (date - wy_start).dt.days + 1
    
    else:
    
        if is_360_day:
            df['day_of_year'] = (df['month'] - 1) * 30 + df['day']
    
        else:
            date = pd.to_datetime(df[['year', 'month', 'day']])
            df['day_of_year'] = date.dt.dayofyear

    if direction=='max':
        idx = df.groupby('year')[flow_cols].idxmax()
    elif direction=='min':
        idx = df.groupby('year')[flow_cols].idxmin()
    else:
        raise Exception("Direction not recognised, must be either 'max' or 'min'")

    peak_days = pd.DataFrame({
        col: df['day_of_year'].reindex(idx[col]).to_numpy()
        for col in flow_cols
    }, index=idx.index)

    peak_days.index.name = 'year'
    
    return peak_days
    


def annual_mean(df, flow_cols):
    
    '''
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.

    Returns
    -------
    mean_flow : pandas dataframe
        Dataframe containing year, and flow columns. Values are the annual mean flow.

    '''
    
    mean_flow = df.groupby('year')[flow_cols].mean()

    mean_flow = mean_flow.round(3)

    mean_flow = mean_flow.astype({
        col: 'float32'
        for col in mean_flow.select_dtypes(include=['float64']).columns
    })
    
    return mean_flow




def monthly_mean(df, flow_cols):
    '''
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.

    Returns
    -------
    mean_flow : pandas dataframe
        Dataframe containing year, month, and flow columns. Values are the mean flow for that year-month.

    '''
    
    mean_flow = df.groupby(['year','month'])[flow_cols].mean()
    
    mean_flow = mean_flow.round(3)

    mean_flow = mean_flow.astype({
        col: 'float32'
        for col in mean_flow.select_dtypes(include=['float64']).columns
    })
    
    return mean_flow
    


def seasonal_mean(df, flow_cols, fix_seasons=True):
    '''
    Compute seasonal mean flow values from a DataFrame containing monthly flow data.

    Group monthly flow data into meteorological seasons (DJF, MAM, JJA, SON)
    Compute mean values for the specified flow columns. 
    It can adjust the December year values so that seasons are continuous across calendar years.

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    fix_seasons : boolean, optional
        Default is True
        If True, adjusts December’s year by +1 to create continuous DJF seasons across years.
        If False, keeps DJF within the same calendar year.
        e.g.
        for fix_seasons = True,  the DJF for 1981 will be Dec 1980, Jan 1981, Feb 1981.
        for fix_seasons = False, the DJF for 1981 will be Jan 1981, Feb 1981, Dec 1981.

    Returns
    -------
    mean_flow : pandas dataframe
        Dataframe containing year, season, and flow columns. Values are the mean flow for that year-season.
    '''
    
    
    month_to_season = {
        12: "DJF", 1: "DJF", 2: "DJF",
        3: "MAM", 4: "MAM", 5: "MAM",
        6: "JJA", 7: "JJA", 8: "JJA",
        9: "SON", 10: "SON", 11: "SON",
    }
    df = df.copy()
    df["season"] = df["month"].map(month_to_season)

    # Adjust December year if seasons should be continuous
    if fix_seasons:
        df.loc[df["month"] == 12, "year"] += 1
    
    mean_flow = df.groupby(['year','season'])[flow_cols].mean()
    
    mean_flow = mean_flow.round(3)

    mean_flow = mean_flow.astype({
        col: 'float32'
        for col in mean_flow.select_dtypes(include=['float64']).columns
    })
    
    return mean_flow



def long_term_mean(df, flow_cols, window_start=None, window_end=None):
    '''
    
    Function for calculating long term mean of daily flows for a given window
    

    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    window_start : integer, optional
        Year for start of flow duration curve window, if None it will take the earliest year in the dataset. Default is None.
    window_end : integer, optional
        Year for end of flow duration curve window, if None it will take the latest year in the dataset. Default is None.

    Returns
    -------
    mean_flow : pandas dataframe
        dataframe of mean flow values for each dat of the year, used to plot an average hydrograph.

    '''
    
    all_years = sorted(df['year'].dropna().unique())
    
    if window_start==None:
        window_start=all_years[0]
        
    if window_end==None:
        window_end=all_years[-1]
    
    window_df = df[(df['year'] >= window_start) & (df['year'] <= window_end)]
    
    mean_flow = window_df.groupby(['month', 'day'])[flow_cols].mean()
    
    mean_flow = mean_flow.round(3)

    mean_flow = mean_flow.astype({
        col: 'float32'
        for col in mean_flow.select_dtypes(include=['float64']).columns
    })
    
    return mean_flow




def nday_flows(df, flow_cols, n=7, direction='max', wy=True):
    '''
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    n : int
        number of days for averaging over
    direction: 'max' or 'min'
        whether to do n day max or min flows
        
    Returns
    -------
    result_df : pandas dataframe
        dataframe containing the minimum or maximum nday flow event in each water year for each rcm.
    
    '''

    df = df.copy()
    # Create a water year column
    df['wy'] = df['year']
    df.loc[df['month']<=9, 'wy'] -= 1

    
    group_col = "wy" if wy else "year"
    group_key = df[group_col]

    roll_means = df.copy()
    roll_means[flow_cols] = (
        df.groupby("wy")[flow_cols]
          .rolling(n, min_periods=n)
          .mean()
          .reset_index(level=0, drop=True)
    )

    records = []

    for col in flow_cols:
        grp = roll_means[col].groupby(group_key.loc[roll_means.index])
            
        for yr, g in grp:
            
            non_na = g.dropna()
            
            # define index type and label
            if non_na.empty:
                continue
            elif direction == "min":
                idx = g.idxmin()
            elif direction == "max":
                idx = g.idxmax()
            else:
                raise Exception("Direction not recognised")

            label_str = direction + " flow"
            flow_label = label_str.title()

            value = g.loc[idx] # min/max value
            
            idx_pos = df.index.get_loc(idx)
            
            # Extract date info from original df
            start_date = df.iloc[idx_pos-(n-1)]

            records.append({
                "Start Year": start_date["year"],
                "Start Month": start_date["month"],
                "Start Day": start_date["day"],
                "Water Year": yr,
                "flowcol": col,
                flow_label: value,
                })

    result_df = pd.DataFrame(records)

    result_df = result_df.round(3)

    result_df = result_df.astype({
        col: 'float32'
        for col in result_df.select_dtypes(include=['float64']).columns
    })
    
    return result_df
    

def transition_event_extraction(df, flow_cols, upper_quant, lower_quant, baseline_start=1991, baseline_end=2020):
    '''
    Parameters
    ----------
    df : pandas dataframe
        Dataframe containing year, month, day columns and columns with flow values.
    flow_cols : list
        list of column names containing flow values.
    upper_quant : int
        quantile for upper threshold
    lower_quant: int
        quantile for upper threshold
    baseline_start : integer, optional
        Start year of the period to use as baseline for calculating the quantile threshold. Default is 1991.
    baseline_end : integer, optional
        End year of the period to use as baseline for calculating the quantile threshold. Default is 2020.
        
    Returns
    -------
    transition_events : pandas dataframe
        dataframe containing all transition events for each rcm.
    '''
    df = df.copy()
    
    #df['day_index'] = (df['year'] - df['year'].min()) * 360 + (df['month'] - 1) * 30 + (df['day'] - 1)
    df['day_index'] = range(len(df['year']))

    baseline_df = df[(df['year'] >= baseline_start) & (df['year'] <= baseline_end)]

    upper_threshold = (100-upper_quant)/100
    lower_threshold = (100-lower_quant)/100

    upper_thresh_df = baseline_df[flow_cols].quantile(upper_threshold)
    lower_thresh_df = baseline_df[flow_cols].quantile(lower_threshold)

    upper_events = df[flow_cols] > upper_thresh_df
    lower_events = df[flow_cols] < lower_thresh_df

    def extract_transitions(col):

        vals = df[col].values
        low = lower_events[col].values
        high = upper_events[col].values

        # Identify continuous low-event segments
        low_groups = (low != np.roll(low, 1)).cumsum()
        low_groups[~low] = 0
        
        low_segments = []
        for g in np.unique(low_groups):
            if g == 0:
                continue
            idx = np.where(low_groups == g)[0]
            low_segments.append(idx)

        # Identify continuous high-event segments
        high_groups = (high != np.roll(high, 1)).cumsum()
        high_groups[~high] = 0

        high_segments = []
        for g in np.unique(high_groups):
            if g == 0:
                continue
            idx = np.where(high_groups == g)[0]
            high_segments.append(idx)

        # Set up list of segments in time order
        segments = []

        # Add low segments to list
        for seg in low_segments:
            segments.append(("low", seg[0], seg[-1]))

        # Add high segments to list
        for seg in high_segments:
            segments.append(("high", seg[0], seg[-1]))

        # Sort segments by starting day
        segments.sort(key=lambda x: x[1])

        results = []

        # Loop through segments in order
        for i, (stype, s_start, s_end) in enumerate(segments):

            # Only consider low segments
            if stype != "low":
                continue

            # There must be a next segment to examine
            if i + 1 >= len(segments):
                continue

            next_stype, next_start, next_end = segments[i+1]

            # Only accept if the next segment is a high segment
            if next_stype != "high":
                continue  # Skip if it's low-low

            last_low_day = s_end
            first_high_day = next_start

            # Calculate magnitude (flow first high day - flow last low day)
            low_last_value = vals[last_low_day]
            high_first_value = vals[first_high_day]
            magnitude = high_first_value - low_last_value

            # Calculate duration
            last_low_ind = df.index[last_low_day]
            first_high_ind = df.index[first_high_day]
            duration = df.loc[first_high_ind, "day_index"] - df.loc[last_low_ind, "day_index"]

            results.append({
                "Start Year":   df.loc[last_low_ind, "year"],
                "Start Month":  df.loc[last_low_ind, "month"],
                "Start Day":    df.loc[last_low_ind, "day"],
                "flowcol":      col,
                "Transition Duration": duration,
                "Transition Magnitude": magnitude
            })

        return pd.DataFrame(results)

    # Apply to all flow columns
    transition_events = pd.concat([extract_transitions(col) for col in flow_cols], ignore_index=True)
    transition_events = transition_events.round(3)
    
    transition_events = transition_events.astype({
        col: 'float32'
        for col in transition_events.select_dtypes(include=['float64']).columns
    })
    
    return transition_events