from calendar import isleap
from datetime import datetime
from datetime import timezone
import numpy as np

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
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y')
    elif timestep_size >= 2419198:
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m')
    elif timestep_size >= 86398:
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d')
    elif timestep_sizeord >= 58:
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M')
    else:
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')







def get_list_of_times(simulation_start_time, simulation_end_time, timestep_size):
    if timestep_size % 31622400 == 0:
        # increment by number_of_years
        number_of_years_per_timestep = int(timestep_size/31622400)
        number_of_timesteps = int(np.ceil((simulation_end_time - simulation_start_time)/timestep_size))
        times = [simulation_start_time]
        
        for period in range(number_of_timesteps):
            new_datetime = datetime.utcfromtimestamp(times[period])
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
            new_datetime = datetime.utcfromtimestamp(times[period])
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