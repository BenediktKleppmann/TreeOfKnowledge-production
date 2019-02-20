import json
import traceback
import pandas as pd
from collection.models import Uploaded_dataset, Attribute, Simulation_model, Object, Data_point
from django.utils.safestring import mark_safe
import os

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
        table_body = data_table_df.to_dict('list')  
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



# called from upload_data7
def perform_uploading(uploaded_dataset, request):
    number_of_datapoints_saved = 0;

    object_type_id = uploaded_dataset.object_type_id

    data_quality = uploaded_dataset.correctness_of_data
    attribute_selection = json.loads(uploaded_dataset.attribute_selection)
    object_identifiers = json.loads(uploaded_dataset.object_identifiers)

    valid_times = json.loads(uploaded_dataset.data_table_json)
    data_table_json = json.loads(uploaded_dataset.data_table_json)
    table_body = data_table_json["table_body"]
    number_of_entities = len(table_body[0])

    

    # prepare list of data types
    data_types = []
    for attribute_id in attribute_selection:
        attribute_record = Attribute.objects.get(id=attribute_id)
        data_types.append(attribute_record.data_type)


    for entity_nb in range(number_of_entities):

        if (object_identifiers[entity_nb] is not None):
            object_id = object_identifiers[entity_nb]
        else:
            object_record = Object(object_type_id=object_type_id)
            object_record.save()
            object_id = object_record.id

        for column_number, attribute_id in enumerate(attribute_selection):
            value = table_body[column_number][entity_nb]
            valid_time_start = valid_times[column_number][entity_nb]['start']
            valid_time_end = valid_times[column_number][entity_nb]['end']

            if attribute_value is not None:
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
    model_id = simulation_model.id

    return (model_id, number_of_datapoints_saved)
