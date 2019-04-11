import json
import traceback
import pandas as pd
from collection.models import Uploaded_dataset, Attribute, Simulation_model, Object, Data_point
from django.utils.safestring import mark_safe
import os
from itertools import compress
import dateutil.parser
import time

# called from upload_data1
def save_new_upload_details(request):
    errors = []
    upload_error = False
    upload_id = None
    try:
        user = request.user
        file_path = request.FILES['file'].name
        file_name = os.path.basename(file_path)
        
        sep = request.POST.get('sep', ',')
        encoding =  request.POST.get('encoding')
        quotechar = request.POST.get('quotechar', '"')
        escapechar = request.POST.get('escapechar')
        na_values = request.POST.get('na_values')
        skiprows = request.POST.get('skiprows')
        header = request.POST.get('header', 'infer')

        # File to JSON -----------------------------------------
        data_table_df = pd.read_csv(request.FILES['file'], sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header)
        data_table_df = data_table_df.where(pd.notnull(data_table_df), None)


        table_header = list(data_table_df.columns)
        table_body = data_table_df.to_dict()  
        for column_number, column_name in enumerate(table_header): # change the table_body-dict to have column_numbers as keys instead of column_nmaes
            table_body[column_number] = table_body.pop(column_name)
        
        data_table_dict = {"table_header": table_header, "table_body": table_body}
        data_table_json = json.dumps(data_table_dict)


        # create record in Uploaded_dataset-table -----------------------------------
        uploaded_dataset = Uploaded_dataset(file_name=file_name, file_path=file_path, sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header, data_table_json=data_table_json, user=user)
        uploaded_dataset.save()
        upload_id = uploaded_dataset.id

    except Exception as error: 
        traceback.print_exc()
        errors = [str(error) + "||||||" + file_path]
        upload_error = True

    return (upload_id, upload_error, errors)


# called from upload_data1
def save_existing_upload_details(upload_id, request):
    errors = []
    upload_error = False
    try:
        uploaded_dataset = Uploaded_dataset.objects.select_for_update().filter(id=upload_id)

        user = request.user
        file_path = request.FILES['file'].name
        file_name = os.path.basename(file_path)
        
        sep = request.POST.get('sep', ',')
        encoding =  request.POST.get('encoding')
        quotechar = request.POST.get('quotechar', '"')
        escapechar = request.POST.get('escapechar')
        na_values = request.POST.get('na_values')
        skiprows = request.POST.get('skiprows')
        header = request.POST.get('header', 'infer')

        # File to JSON -----------------------------------------
        data_table_df = pd.read_csv(request.FILES['file'], sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header)
        data_table_df = data_table_df.where(pd.notnull(data_table_df), None)

        table_header = list(data_table_df.columns)
        table_body = data_table_df.to_dict('list')  
        for column_number, column_name in enumerate(table_header): # change the table_body-dict to have column_numbers as keys instead of column_nmaes
            table_body[column_number] = table_body.pop(column_name)
        
        data_table_dict = {"table_header": table_header, "table_body": table_body}
        data_table_json = json.dumps(data_table_dict)

        uploaded_dataset.update(file_name=file_name, file_path=file_path, sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header, data_table_json=data_table_json, user=user)

    except Exception as error:
        traceback.print_exc()
        errors = [str(error)]
        upload_error = True
    
    return (upload_error, errors)


# called from upload_data6A and 6B
def make_table_attributes_dict(uploaded_dataset):
    selected_attribute_ids = json.loads(uploaded_dataset.attribute_selection)
    table_attributes = []
    for attribute_id in selected_attribute_ids:
        attribute_record = Attribute.objects.get(id=attribute_id)
        table_attributes.append({'attribute_id':attribute_id, 'attribute_name':attribute_record.name})
    return table_attributes


# called from upload_data6B
def make_data_table_json_with_distinct_entities(uploaded_dataset):
    """
    The uploaded table is timeseries data that has multiple records (= rows) for the same entity. 
    (Usually, each row describes the entity at a different timestep).
    In upload_data6 the user is asked to match the entities described in the table to existing entities in the knowledge base. 
    So that the user only has to match each entity once, we here merge the data for one entity into one record.
    """
    
    object_identifiers = json.loads(uploaded_dataset.object_identifiers)
    data_table_json = json.loads(uploaded_dataset.data_table_json)
    table_df = pd.DataFrame(data_table_json['table_body'])

    columns = list(table_df.columns)
    idenifying_columns = list(compress(columns, object_identifiers))
    aggregation_dict = {column:'first' for column in columns}
    aggregated_table_df = table_df.groupby(idenifying_columns).aggregate(aggregation_dict)

    new_table_body = aggregated_table_df.to_dict('list') 
    data_table_json['table_body'] = new_table_body

    return data_table_json



# called from upload_data7
def perform_uploading(uploaded_dataset, request):
    """
        Main upload function for non-timeseries data.
    """


    number_of_datapoints_saved = 0;

    object_type_id = uploaded_dataset.object_type_id

    data_quality = uploaded_dataset.correctness_of_data
    attribute_selection = json.loads(uploaded_dataset.attribute_selection)

    list_of_matches = json.loads(uploaded_dataset.list_of_matches)

    valid_time_start = int(time.mktime(uploaded_dataset.data_generation_date.timetuple()))
    data_table_json = json.loads(uploaded_dataset.data_table_json)
    table_body = data_table_json["table_body"]

    number_of_entities = len(table_body[list(table_body.keys())[0]])
     


    # prepare list of data_types and of expected_valid_periods
    data_types = []
    valid_times_end = []
    for attribute_id in attribute_selection:
        attribute_record = Attribute.objects.get(id=attribute_id)
        data_types.append(attribute_record.data_type)
        valid_times_end.append(valid_time_start + attribute_record.expected_valid_period)


    for entity_nb in range(number_of_entities):

        if (list_of_matches[entity_nb] is not None):
            object_id = list_of_matches[entity_nb]
        else:
            object_record = Object(object_type_id=object_type_id)
            object_record.save()
            object_id = object_record.id

        for column_number, attribute_id in enumerate(attribute_selection):
            value = table_body[str(column_number)][entity_nb]
            valid_time_end = valid_times_end[column_number]

            if value is not None:
                value_as_string = str(value)

                if data_types[column_number] == "string":             
                    numeric_value = None
                    string_value = value
                    boolean_value = None
                elif data_types[column_number] in ["int", "real"]: 
                    numeric_value = value
                    string_value = None
                    boolean_value = None
                elif data_types[column_number] == "bool": 
                    numeric_value = value
                    string_value = None
                    boolean_value = None

                data_point_record = Data_point( object_id=object_id, 
                                                attribute_id=attribute_id, 
                                                value_as_string=value_as_string, 
                                                numeric_value=numeric_value, 
                                                string_value=string_value, 
                                                boolean_value=boolean_value, 
                                                valid_time_start=valid_time_start, 
                                                valid_time_end=valid_time_end, 
                                                data_quality=data_quality)
                data_point_record.save()
                number_of_datapoints_saved += 1


    object_type_record = Object_types.objects.get(id=object_type_id)
    objects_dict = {}
    objects_dict[1] = { 'object_name':object_type_record.name + ' 1', 
                        'object_type_id':object_type_id, 
                        'object_type_name':object_type_record.name, 
                        'object_icon':object_type_record.object_icon, 
                        'object_attributes':{},
                        'object_filter_facts':uploaded_dataset.meta_data_facts,
                        'position':{'x':100, 'y':100},
                        'get_new_object_data': True};
    simulation_model = Simulation_model(user=request.user, 
                                        objects_dict=json.dumps(objects_dict),
                                        object_type_counts=json.dumps({object_type_id:1}),
                                        total_object_count=0,
                                        number_of_additional_object_facts=2,
                                        simulation_start_time=946684800, 
                                        simulation_end_time=1577836800, 
                                        timestep_size=31536000,
                                        runtime_value_correction=False)
    simulation_model.save()
    new_model_id = simulation_model.id

    return (number_of_datapoints_saved, new_model_id)


# called from upload_data7
def perform_uploading_for_timeseries(uploaded_dataset, request):
    """
        Main upload function for timeseries data.

    Note: the valid times are determined as follows...
    The start time is the measurement time.
    The ending time is the smaller of the following two:
        * the next measurement time for this object (minus 1 second)(if it exists)
        * the start time plus the expected_valid_period of the attribute
    """
    number_of_datapoints_saved = 0;


    # get the values from uploaded_dataset
    object_type_id = uploaded_dataset.object_type_id
    list_of_matches = json.loads(uploaded_dataset.list_of_matches)
    attribute_selection = json.loads(uploaded_dataset.attribute_selection)
    datetime_column = json.loads(uploaded_dataset.datetime_column)
    data_quality = uploaded_dataset.correctness_of_data

    # prepare list of data_types and of expected_valid_periods
    data_types = []
    expected_valid_periods = []
    for attribute_id in attribute_selection:
        attribute_record = Attribute.objects.get(id=attribute_id)
        data_types.append(attribute_record.data_type)
        expected_valid_periods.append(attribute_record.expected_valid_period)


    # the submitted table
    submitted_data_table_json = json.loads(uploaded_dataset.data_table_json)
    submitted_data_table_df = pd.DataFrame(submitted_data_table_json['table_body'])
    columns = list(submitted_data_table_df.columns)

    # add the column 'valid_time_start'
    valid_time_start_column = []
    for date_string in datetime_column:
        date_time = dateutil.parser.parse(date_string)
        valid_time_start_column.append(int(time.mktime(date_time.timetuple())))
    submitted_data_table_df['valid_time_start'] = valid_time_start_column



    # add the columns 'object_id', 'measurement_times' and 'measurement_number'
    if uploaded_dataset.object_identifiers is not None:
        # 1. object_id
        object_identifiers = json.loads(uploaded_dataset.object_identifiers)
        grouped_data_table_json = make_data_table_json_with_distinct_entities(uploaded_dataset)
        object_ids_df = pd.DataFrame(grouped_data_table_json['table_body'])
        object_ids_df['object_id'] = list_of_matches

        for index, row in object_ids_df.iterrows():
            if row['object_id'] is None:
                object_record = Object(object_type_id=object_type_id)
                object_record.save()
                object_ids_df.ix[index, 'object_id'] = object_record.id

        join_columns = list(compress(columns, object_identifiers))
        object_ids_df = object_ids_df[join_columns + ['object_id']]
        submitted_data_table_df = pd.merge(submitted_data_table_df, object_ids_df, on=join_columns, how='left')

        # 2. measurement_times
        measurement_times_df = submitted_data_table_df.groupby(join_columns)['valid_time_start'].apply(list).to_frame()
        measurement_times_df.reset_index(inplace=True) 
        measurement_times_df = measurement_times_df.rename(index=str, columns={'valid_time_start': 'measurement_times'})
        submitted_data_table_df = pd.merge(submitted_data_table_df, measurement_times_df, on=join_columns, how='left')

        # 3. measurement_number
        submitted_data_table_df = submitted_data_table_df.sort_values(join_columns + ['valid_time_start'])
        submitted_data_table_df['measurement_number'] = submitted_data_table_df.groupby(join_columns).cumcount()+1

    else: 
        # 1. object_id
        submitted_data_table_df['object_id'] = list_of_matches
        for row_number, row in submitted_data_table_df.iterrows():
            if row['object_id'] is None:
                object_record = Object(object_type_id=object_type_id)
                object_record.save()
                submitted_data_table_df.ix[index, 'object_id'] = object_record.id

        # 2. measurement_times
        submitted_data_table_df['measurement_times'] = [[time] for time in submitted_data_table_df['valid_time_start']]

        # 3. measurement_number
        submitted_data_table_df['measurement_number'] = 1




    # loop through rows and values 
    for row_nb, row in submitted_data_table_df.iterrows():
        print("row_nb: " + str(row_nb))
            
        object_id = row['object_id']

        for column_number, column in enumerate(columns):
            attribute_id = attribute_selection[column_number]
            value = row[column]
            valid_time_start = row['valid_time_start']
            expected_end_time = valid_time_start + expected_valid_periods[column_number]
            if row['measurement_number'] < len(row['measurement_times']):
                next_measurement_time = row['measurement_times'][row['measurement_number']] # row['measurement_number'] is the index of the next measurement number, because the indexes start at 0 instead of 1
                valid_time_end = min(next_measurement_time, expected_end_time)
            else:
                valid_time_end = expected_end_time


            if value is not None:
                value_as_string = str(value)

                if data_types[column_number] == "string":             
                    numeric_value = None
                    string_value = value
                    boolean_value = None
                elif data_types[column_number] in ["int", "real"]: 
                    numeric_value = value
                    string_value = None
                    boolean_value = None
                elif data_types[column_number] == "bool": 
                    numeric_value = value
                    string_value = None
                    boolean_value = None


                data_point_record = Data_point( object_id=object_id, 
                                                attribute_id=attribute_id, 
                                                value_as_string=value_as_string, 
                                                numeric_value=numeric_value, 
                                                string_value=string_value, 
                                                boolean_value=boolean_value, 
                                                valid_time_start=valid_time_start, 
                                                valid_time_end=valid_time_end, 
                                                data_quality=data_quality)
                data_point_record.save()
                number_of_datapoints_saved += 1


    simulation_model = Simulation_model(user=request.user, name="", description="", meta_data_facts=uploaded_dataset.meta_data_facts)
    simulation_model.save()
    new_model_id = simulation_model.id

    return (number_of_datapoints_saved, new_model_id)
