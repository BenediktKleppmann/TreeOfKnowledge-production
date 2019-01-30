import json
import traceback
import pandas as pd
from collection.models import Uploaded_dataset, Attribute
from django.utils.safestring import mark_safe
import os


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
        # data_table_json = simplejson.dumps(data_table_dict, ignore_nan=True)
        # data_table_json = mark_safe(data_table_json)


        # create record in Uploaded_dataset-table -----------------------------------
        uploaded_dataset = Uploaded_dataset(file_name=file_name, file_path=file_path, sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header, data_table_json=data_table_json, user=user)
        uploaded_dataset.save()
        upload_id = uploaded_dataset.id

    except Exception as error: 
        traceback.print_exc()
        errors = [str(error) + "||||||" + file_path]
        upload_error = True

    return (upload_id, upload_error, errors)


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
        # data_table_json = simplejson.dumps(data_table_dict, ignore_nan=True)
        # data_table_json = data_table_json.replace('&quot;','"')
        # data_table_json = mark_safe(data_table_json)

        uploaded_dataset.update(file_name=file_name, file_path=file_path, sep=sep, encoding=encoding, quotechar=quotechar, escapechar=escapechar, na_values=na_values, skiprows=skiprows, header=header, data_table_json=data_table_json, user=user)

    except Exception as error:
        traceback.print_exc()
        errors = [str(error)]
        upload_error = True

    # except Exception as error: 
    #     errors = [str(error)]
    #     upload_error = True
    #     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #     print(error)
    #     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    return (upload_error, errors)




def perform_uploading(uploaded_dataset, request):




    simulation_model = Simulation_model(user=request.user, name="", description="")
    simulation_model.save()
    model_id = uploaded_dataset.id

    # Add the Meta Data Constraints to the simulation
    attribute = Attribute.objects.get(id=uploaded_dataset.attribute1)
    if ((attribute is not None) and (uploaded_dataset.operation1 in ['=','>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation1, value=uploaded_dataset.value1)
    
    attribute = Attribute.objects.get(id=uploaded_dataset.attribute2)
    if ((attribute is not None) and (uploaded_dataset.operation2 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation2, value=uploaded_dataset.value2)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute3)
    if ((attribute is not None) and (uploaded_dataset.operation3 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation3, value=uploaded_dataset.value3)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute4)
    if ((attribute is not None) and (uploaded_dataset.operation4 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation4, value=uploaded_dataset.value4)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute5)
    if ((attribute is not None) and (uploaded_dataset.operation5 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation5, value=uploaded_dataset.value5)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute6)
    if ((attribute is not None) and (uploaded_dataset.operation6 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation6, value=uploaded_dataset.value6)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute7)
    if ((attribute is not None) and (uploaded_dataset.operation7 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation7, value=uploaded_dataset.value7)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute8)
    if ((attribute is not None) and (uploaded_dataset.operation8 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation8, value=uploaded_dataset.value8)

    attribute = Attribute.objects.get(id=uploaded_dataset.attribute9)
    if ((attribute is not None) and (uploaded_dataset.operation9 in ['=', '>', '<', 'in'])):
        meta_data_constaint = Meta_data_constaint(simulation_model=simulation_model, attribute=attribute, operation=uploaded_dataset.operation9, value=uploaded_dataset.value9)

    # ETC...

    return model_id
