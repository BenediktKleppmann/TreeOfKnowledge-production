####################################################################
# This file is part of the Tree of Knowledge project.
# Copyright (c) 2019-2040 Benedikt Kleppmann

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version - see http://www.gnu.org/licenses/.
#####################################################################

from calendar import isleap
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import numpy as np
import pandas as pd
import pdb



def intersections(row):
    """
        I got this function from https://stackoverflow.com/questions/40367461/intersection-of-two-lists-of-ranges-in-python/40368017
        Haven't checked it yet ...
    """
    a = row['valid_range']
    b = row['new_valid_range']

    ranges = []
    i = j = 0
    while i < len(a) and j < len(b):
        a_left, a_right = a[i]
        b_left, b_right = b[j]

        if a_right < b_right:
            i += 1
        else:
            j += 1

        if a_right >= b_left and b_right >= a_left:
            end_pts = sorted([a_left, a_right, b_left, b_right])
            middle = [end_pts[1], end_pts[2]]
            ranges.append(middle)

    ri = 0
    while ri < len(ranges)-1:
        if ranges[ri][1] == ranges[ri+1][0]:
            ranges[ri:ri+2] = [[ranges[ri][0], ranges[ri+1][1]]]

        ri += 1

    return ranges



def unix_timestamp_to_string(unix_timestamp, timestep_size):
    
    if timestep_size >= 31535998:
        as_datetime = datetime(1970, 1, 1) + timedelta(seconds=unix_timestamp)
        return as_datetime.strftime('%Y')
        # return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y')
    elif timestep_size >= 2419198:
        as_datetime = datetime(1970, 1, 1) + timedelta(seconds=unix_timestamp)
        return as_datetime.strftime('%Y-%m')
        # return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m')
    elif timestep_size >= 86398:
        as_datetime = datetime(1970, 1, 1) + timedelta(seconds=unix_timestamp)
        return as_datetime.strftime('%Y-%m-%d')
        # return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d')
    elif timestep_sizeord >= 58:
        as_datetime = datetime(1970, 1, 1) + timedelta(seconds=unix_timestamp)
        return as_datetime.strftime('%Y-%m-%d %H:%M')
        # return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M')
    else:
        as_datetime = datetime(1970, 1, 1) + timedelta(seconds=unix_timestamp)
        return as_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')




def deduplicate_list_of_dicts(list_of_dicts):
    seen = set()
    new_list = []
    for dictionary in list_of_dicts:
        tup = tuple(dictionary.items())
        if tup not in seen:
            seen.add(tup)
            new_list.append(dictionary)
    return new_list


def get_list_of_times(simulation_start_time, simulation_end_time, timestep_size):
    if timestep_size % 31622400 == 0:
        # increment by number_of_years
        number_of_years_per_timestep = int(timestep_size/31622400)
        number_of_timesteps = int(np.ceil((simulation_end_time - simulation_start_time)/timestep_size))
        times = [simulation_start_time]
        
        for period in range(number_of_timesteps):
            new_datetime = datetime(1970, 1, 1) + timedelta(seconds=times[period])
            # new_datetime = datetime.utcfromtimestamp()
#             print('before: ' + str(new_datetime))
            new_datetime = add_years(new_datetime, number_of_years_per_timestep)
#             print('after: ' + str(new_datetime))
            new_timestamp = int(new_datetime.replace(tzinfo=timezone.utc).timestamp())
            times.append(new_timestamp)
            
    elif timestep_size % 2635200 == 0:
        # increment by number_of_months
        number_of_months_per_timestep = int(timestep_size/2635200)
        number_of_timesteps = int(np.ceil((simulation_end_time - simulation_start_time)/timestep_size))
        times = [simulation_start_time]
        
        for period in range(number_of_timesteps):
            new_datetime = datetime(1970, 1, 1) + timedelta(seconds=times[period])
            # new_datetime = datetime.utcfromtimestamp(times[period])
            new_datetime = add_months(new_datetime, number_of_months_per_timestep)
            new_timestamp = int(new_datetime.replace(tzinfo=timezone.utc).timestamp())
            times.append(new_timestamp)

    else:        
        times = np.arange(simulation_start_time, simulation_end_time, timestep_size)
        
    return times





def add_years(d, years):
    new_year = d.year + years
    try:
        return d.replace(year=new_year)
    except ValueError:
        if (d.month == 2 and d.day == 29 and # leap day
            isleap(d.year) and not isleap(new_year)):
            return d.replace(year=new_year, day=28)
        raise

   

        
def add_months(d, months):
    new_month = d.month + months
    new_year = d.year
    if new_month > 12:
        new_month = new_month%12
        new_year = new_year + int(new_month/12)
    try:
        return d.replace(year=new_year, month=new_month)
    except ValueError:
        if (d.month == 2 and d.day == 29 and # leap day
            isleap(d.year) and not isleap(new_year)):
            return d.replace(year=new_year, month=new_month, day=28)
        raise



# ================================================================================
#  Decorators
# ================================================================================        


def cash_result(func):
    def inner(objects_dict, times, timestep_size):
        store = pd.HDFStore('C:/Users/l412/Documents/1 projects/2020-05-21 Lifecycle Simulation/data/HDFStore.h5')
        cash_name = str(objects_dict) + '_' + str(times) + '_' + str(timestep_size)
        if cash_name in store.keys():
            return store[cash_name]
        else:
            df = func(objects_dict, times, timestep_size) 
            store[cash_name] = df
            return df
    return inner

