from datetime import datetime


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




