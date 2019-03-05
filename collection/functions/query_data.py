from collection.models import Object_types, Attribute, Object, Data_point
import numpy as np
import pandas as pd
from datetime import datetime
from collection.functions import generally_useful_functions, get_from_db

def get_data_points(object_type_id, filter_facts, specified_start_time, specified_end_time):
    nothing_found_response = {}
    nothing_found_response['table_body'] = {}
    nothing_found_response['table_attributes'] = []
    nothing_found_response['number_of_entities_found'] = 0

    # PART 1: For each Object_id find the time ranges where all the Filter-Fact Conditions are fulfilled
    # basic filtering: object_type and specified time range
    child_object_types = get_from_db.get_list_of_child_objects(object_type_id)
    child_object_ids = [el['id'] for el in child_object_types]
    objects_with_suitable_otype = Object.objects.filter(object_type_id__in=child_object_ids).values_list('id', flat=True)
    data_point_records = Data_point.objects.filter(object_id__in=objects_with_suitable_otype)
    data_point_records = data_point_records.filter(valid_time_start__gte=specified_start_time, valid_time_start__lt=specified_end_time)           

    # apply filter-facts
    object_ids = list(data_point_records.values_list('object_id', flat=True))
    valid_ranges_df = pd.DataFrame({'object_id':object_ids})
    valid_ranges_df['valid_range'] = [[[specified_start_time,specified_end_time]] for i in valid_ranges_df.index]

    for filter_fact in filter_facts:
        if filter_fact['operation'] == '=':
            filtered_data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],string_value=str(filter_fact['value']))           
        elif filter_fact['operation'] == '>':
            filtered_data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],numeric_value__gt=filter_fact['value'])           
        elif filter_fact['operation'] == '<':
            filtered_data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],numeric_value__lt=filter_fact['value'])           
        elif filter_fact['operation'] == 'in':
            values = [str(value) for value in filter_fact['value']]
            filtered_data_point_records = data_point_records.filter(attribute_id=filter_fact['attribute_id'],string_value__in=values)           

        # find the intersecting time ranges (= the overlap between the known valid_ranges and the valid_ranges from the new filter fact)
        filtered_data_points_df = pd.DataFrame(list(filtered_data_point_records.values('object_id','valid_time_start','valid_time_end')))
        if len(filtered_data_points_df) == 0:
            return nothing_found_response
        filtered_data_points_df = filtered_data_points_df.sort_values(['object_id','valid_time_start'])
        filtered_data_points_df['new_valid_range'] = list(zip(filtered_data_points_df['valid_time_start'],filtered_data_points_df['valid_time_end']))
        new_valid_ranges_df = pd.DataFrame(filtered_data_points_df.groupby('object_id')['new_valid_range'].apply(list)) # for every object_id there now is a list of valid ranges
        new_valid_ranges_df['object_id']  = new_valid_ranges_df.index

        valid_ranges_df = pd.merge(valid_ranges_df, new_valid_ranges_df, on='object_id', how='left')
        valid_ranges_df = valid_ranges_df[valid_ranges_df['new_valid_range'].notnull()]
        valid_ranges_df['valid_range'] = valid_ranges_df.apply(generally_useful_functions.intersections, axis=1)
        # valid_ranges_df['valid_range'] = np.vectorize(generally_useful_functions.intersections)(valid_ranges_df['valid_range'], valid_ranges_df['new_valid_range'])
        valid_ranges_df = valid_ranges_df[['object_id', 'valid_range']]


    # choose the first time interval that satisfies all filter-fact conditions
    valid_ranges_df['satisfying_time_start'] = [object_ranges[0][0] for object_ranges in valid_ranges_df['valid_range']]
    valid_ranges_df['satisfying_time_end'] = [object_ranges[0][1] for object_ranges in valid_ranges_df['valid_range']]


    # make long table with all datapoints of the found objects
    found_objects = list(set(data_point_records.values_list('object_id', flat=True)))
    if len(found_objects) == 0:
        return nothing_found_response
    all_data_points = Data_point.objects.filter(object_id__in=found_objects)    
    long_table_df = pd.DataFrame(list(all_data_points.values()))

    # filter out the observations from not-satisfying times
    long_table_df = pd.merge(long_table_df, valid_ranges_df, how='left', on='object_id')
    long_table_df = long_table_df[(long_table_df['valid_time_end'] > long_table_df['satisfying_time_start']) & (long_table_df['valid_time_start'] < long_table_df['satisfying_time_end'])]


    # select satisfying time (and remove the records from other times)
    total_data_quality_df = long_table_df.groupby(['object_id','satisfying_time_start']).aggregate({'object_id':'first','satisfying_time_start':'first', 'data_quality': np.sum, 'attribute_id': 'count'})
    total_data_quality_df = total_data_quality_df.rename(columns={"data_quality": "total_data_quality", "attribute_id":"attriubte_count"})

    total_data_quality_df = total_data_quality_df.sort_values(['total_data_quality','satisfying_time_start'], ascending=[False, True])
    total_data_quality_df = total_data_quality_df.drop_duplicates(subset=['object_id'], keep='first')
    long_table_df = pd.merge(long_table_df, total_data_quality_df, how='inner', on=['object_id','satisfying_time_start'])

    # remove the duplicates (=duplicate values within the satisfying time)
    long_table_df['time_difference_of_start'] = abs(long_table_df['satisfying_time_start'] - long_table_df['valid_time_start'])
    long_table_df = long_table_df.sort_values(['data_quality','time_difference_of_start'], ascending=[False, True])
    long_table_df = long_table_df.drop_duplicates(subset=['object_id','attribute_id'], keep='first')

    # pivot the long table
    long_table_df = long_table_df.reindex()
    long_table_df = long_table_df[['object_id','satisfying_time_start','attribute_id', 'string_value', 'numeric_value','boolean_value' ]]
    long_table_df.set_index(['object_id','satisfying_time_start','attribute_id'],inplace=True)
    broad_table_df = long_table_df.unstack('attribute_id')

    # there are columns for the different datatypes, determine which to keep
    columns_to_keep = []
    for column in broad_table_df.columns:
        attribute_data_type = Attribute.objects.get(id=column[1]).data_type
        if attribute_data_type=='string' and column[0]=='string_value':
            columns_to_keep.append(column)
        elif attribute_data_type in ['real', 'int'] and column[0]=='numeric_value':
            columns_to_keep.append(column)
        elif attribute_data_type == 'boolean' and column[0]=='boolean_value':
            columns_to_keep.append(column)

    broad_table_df = broad_table_df[columns_to_keep]
    new_column_names = [column[1] for column in columns_to_keep]
    broad_table_df.columns = new_column_names
    
    # for response: list of the tables' attributes sorted with best populated first
    table_attributes = []
    sorted_attribute_ids = broad_table_df.isnull().sum(0).sort_values(ascending=False).index
    sorted_attribute_ids = [int(attribute_id) for attribute_id in list(sorted_attribute_ids)]
    for attribute_id in sorted_attribute_ids:
        attribute_record = Attribute.objects.get(id=attribute_id)
        table_attributes.append({'attribute_id':attribute_id, 'attribute_name':attribute_record.name})


    # sort broad_table_df (the best-populated entities to the top)
    broad_table_df = broad_table_df.loc[broad_table_df.isnull().sum(1).sort_values().index]

    # prepare response
    broad_table_df['object_id'] = [val[0] for val in broad_table_df.index]
    broad_table_df['time'] = [datetime.fromtimestamp(val[1]).strftime('%Y-%m-%d') for val in broad_table_df.index] # this is the chosen satisfying_time_start for the object_id
    broad_table_df.reindex()
    broad_table_df = broad_table_df.where(pd.notnull(broad_table_df), None)
    table_body = broad_table_df.to_dict('list')

    response = {}
    response['table_body'] = table_body
    response['table_attributes'] = table_attributes
    response['number_of_entities_found'] = len(found_objects)

    return response





