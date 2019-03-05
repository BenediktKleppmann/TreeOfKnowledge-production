from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset, Object_hierachy_tree_history, Attribute, Object_types, Data_point, Object
from django.db.models import Count
from collection.forms import UserForm, ProfileForm, Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3, Uploaded_datasetForm4, Uploaded_datasetForm5, Uploaded_datasetForm6, Uploaded_datasetForm7
from django.template.defaultfilters import slugify
from collection.functions import upload_data, get_from_db, populate_db, tdda_functions, query_data
from django.http import HttpResponse
import json
import traceback
import csv
import pandas as pd
import xlwt
from django.utils.encoding import smart_str
import time


 # ===============================================================================
 #  _______ _           __          __  _         _ _       
 # |__   __| |          \ \        / / | |       (_) |      
 #    | |  | |__   ___   \ \  /\  / /__| |__  ___ _| |_ ___ 
 #    | |  | '_ \ / _ \   \ \/  \/ / _ \ '_ \/ __| | __/ _ \
 #    | |  | | | |  __/    \  /\  /  __/ |_) \__ \ | ||  __/
 #    |_|  |_| |_|\___|     \/  \/ \___|_.__/|___/_|\__\___|
 # 
 # ===============================================================================                                                         

def landing_page(request):
    return render(request, 'landing_page.html')

def about(request):
    return render(request, 'about.html')

def subscribe(request):
    if request.method == 'POST':
        form_class = Subscriber_registrationForm
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            subscriber = Newsletter_subscriber.objects.get(email=email)
            return redirect('subscriber_page', userid=subscriber.userid)
        else:
            return render(request, 'subscribe.html', {'error_occured': True,})
    else:
        return render(request, 'subscribe.html', {'error_occured': False,})


def contact(request):
    return render(request, 'contact.html')


def subscriber_page(request, userid):
    subscriber = Newsletter_subscriber.objects.get(userid=userid)
    
    is_post_request = False
    if request.method == 'POST':
        is_post_request = True
        form_class = Subscriber_preferencesForm
        form = form_class(data=request.POST, instance=subscriber)
        if form.is_valid():
            form.save()

    return render(request, 'subscriber_page.html', {'subscriber':subscriber, 'is_post_request':is_post_request, })




# ===== THE TOOL ===================================================================
@login_required
def main_menu(request):
    models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tree_of_knowledge_frontend/main_menu.html', {'models': models})


@login_required
def profile_and_settings(request):
    errors = []
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if not user_form.is_valid():
            errors.append('Error: something is wrong with either the first name, last name or email.')
        else:
            if not profile_form.is_valid():
                errors.append('Error: something is wrong with the message-box setting.')
            else:
                user_form.save()
                profile_form.save()
                return redirect('main_menu')
   
    return render(request, 'tree_of_knowledge_frontend/profile_and_settings.html', {'errors': errors})



 # ===============================================================
 #   _    _       _                 _       _       _        
 #  | |  | |     | |               | |     | |     | |       
 #  | |  | |_ __ | | ___   __ _  __| |   __| | __ _| |_ __ _ 
 #  | |  | | '_ \| |/ _ \ / _` |/ _` |  / _` |/ _` | __/ _` |
 #  | |__| | |_) | | (_) | (_| | (_| | | (_| | (_| | || (_| |
 #   \____/| .__/|_|\___/ \__,_|\__,_|  \__,_|\__,_|\__\__,_|
 #         | |                                               
 #         |_|         
 # ===============================================================


@login_required
def upload_data1_new(request):
    errors = []
    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                (upload_id, upload_error, new_errors) = upload_data.save_new_upload_details(request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'upload_error':upload_error, 'errors': errors})
                else:
                    return redirect('upload_data1', upload_id=upload_id)

        # return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})
        return redirect('upload_data1', upload_id=upload_id, errors=errors)
    else:
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})



@login_required
def upload_data1(request, upload_id, errors=[]):
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                (upload_error, new_errors) = upload_data.save_existing_upload_details(upload_id, request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'upload_error':upload_error, 'errors': errors, 'uploaded_dataset':uploaded_dataset})
                else:
                    return redirect('upload_data1', upload_id=upload_id)

    return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})




@login_required
def upload_data2(request, upload_id):
    errors = []
    error_dict = '{}'
    
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
            error_dict = json.dumps(dict(form2.errors))
        else:
            form2.save()
            return redirect('upload_data3', upload_id=upload_id)

    known_data_sources = get_from_db.get_known_data_sources()
    return render(request, 'tree_of_knowledge_frontend/upload_data2.html', {'uploaded_dataset': uploaded_dataset, 'known_data_sources': known_data_sources, 'errors': errors, 'error_dict': error_dict})


@login_required
def upload_data3(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        form3 = Uploaded_datasetForm3(data=request.POST, instance=uploaded_dataset)
        if not form3.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form3.save()
            return redirect('upload_data4', upload_id=upload_id)

    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tree_of_knowledge_frontend/upload_data3.html', {'uploaded_dataset': uploaded_dataset, 'object_hierachy_tree':object_hierachy_tree, 'errors': errors})


@login_required
def upload_data4(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        meta_data_facts_old = json.loads(request.POST['meta_data_facts'])
        meta_data_facts_new = get_from_db.convert_fact_values_to_the_right_format(meta_data_facts_old)
        request.POST._mutable = True
        request.POST['meta_data_facts'] = json.dumps(meta_data_facts_new)

        form4 = Uploaded_datasetForm4(data=request.POST, instance=uploaded_dataset)
        if not form4.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form4.save()
            return redirect('upload_data5', upload_id=upload_id)

    data_generation_year = "2015"
    if uploaded_dataset.data_generation_date is not None:
        data_generation_year = uploaded_dataset.data_generation_date.year
    return render(request, 'tree_of_knowledge_frontend/upload_data4.html', {'uploaded_dataset': uploaded_dataset, 'data_generation_year':data_generation_year, 'errors': errors})




@login_required
def upload_data5(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})
    
    if request.method == 'POST':
        form5 = Uploaded_datasetForm5(data=request.POST, instance=uploaded_dataset)
        if not form5.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form5.save()
            if request.POST.get('datetime_column') is None:
                return redirect('upload_data6A', upload_id=upload_id) #non-timeseries
            else:
                return redirect('upload_data6B', upload_id=upload_id) #timeseries
 
    return render(request, 'tree_of_knowledge_frontend/upload_data5.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def upload_data6A(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form6 = Uploaded_datasetForm6(data=request.POST, instance=uploaded_dataset)
        if not form6.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form6.save()
            return redirect('upload_data7', upload_id=upload_id)
   
    table_attributes = upload_data.make_table_attributes_dict(uploaded_dataset)
    return render(request, 'tree_of_knowledge_frontend/upload_data6.html', {'data_table_json': uploaded_dataset.data_table_json, 'table_attributes': table_attributes, 'errors': errors})



@login_required
def upload_data6B(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form6 = Uploaded_datasetForm6(data=request.POST, instance=uploaded_dataset)
        if not form6.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form6.save()
            (number_of_datapoints_saved, new_model_id) = upload_data.perform_uploading_for_timeseries(uploaded_dataset, request)
            return redirect('upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
   
    
    table_attributes = upload_data.make_table_attributes_dict(uploaded_dataset)
    if uploaded_dataset.object_identifiers is None:
        data_table_json = uploaded_dataset.data_table_json
    else: 
        data_table_json_dict = upload_data.make_data_table_json_with_distinct_entities(uploaded_dataset)
        data_table_json = json.dumps(data_table_json_dict)
    return render(request, 'tree_of_knowledge_frontend/upload_data6.html', {'data_table_json': data_table_json, 'table_attributes': table_attributes, 'errors': errors})




@login_required
def upload_data7(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    
    if request.method == 'POST':
        form7 = Uploaded_datasetForm7(data=request.POST, instance=uploaded_dataset)
        if not form7.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form7.save()
            (number_of_datapoints_saved, new_model_id) = upload_data.perform_uploading(uploaded_dataset, request)
            return redirect('upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
   
    return render(request, 'tree_of_knowledge_frontend/upload_data7.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})


@login_required
def upload_data_success(request, number_of_datapoints_saved, new_model_id):
    all_models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tree_of_knowledge_frontend/upload_data_success.html', {'number_of_datapoints_saved':number_of_datapoints_saved, 'new_model_id':new_model_id, 'all_models': all_models})



 # =================================================================================
 #  _    _      _                   ______                _   _                 
 # | |  | |    | |                 |  ____|              | | (_)                
 # | |__| | ___| |_ __   ___ _ __  | |__ _   _ _ __   ___| |_ _  ___  _ __  ___ 
 # |  __  |/ _ \ | '_ \ / _ \ '__| |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
 # | |  | |  __/ | |_) |  __/ |    | |  | |_| | | | | (__| |_| | (_) | | | \__ \
 # |_|  |_|\___|_| .__/ \___|_|    |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
 #               | |                                                            
 #               |_|                                                          
 # =================================================================================               

# ==================
# GET
# ==================






@login_required
def get_possible_attributes(request):
    object_type_id = request.GET.get('object_type_id', '')
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]

    response = []
    attributes = Attribute.objects.all().filter(first_applicable_object__in=list_of_parent_object_ids)
    for attribute in attributes:
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name})
    return HttpResponse(json.dumps(response))

# used in create_attribute_modal.html
@login_required
def get_list_of_parent_objects(request):
    object_type_id = request.GET.get('object_type_id', '')
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    return HttpResponse(json.dumps(list_of_parent_objects))


# used in edit_attribute_modal.html
@login_required
def get_list_of_objects(request):
    list_of_objects = []
    object_records = Object_types.objects.all()
    for object_record in object_records:
        list_of_objects.append({'id':object_record.id, 'name':object_record.name})
    return HttpResponse(json.dumps(list_of_objects))    


# used in edit_attribute_modal.html
@login_required
def get_attribute_details(request):
    attribute_id = request.GET.get('attribute_id', '')
    attribute_id = int(attribute_id)
    attribute_record = Attribute.objects.get(id=attribute_id)
    attribute_details = {'id':attribute_record.id, 
                'name':attribute_record.name,
                'data_type':attribute_record.data_type,
                'expected_valid_period':attribute_record.expected_valid_period,
                'description':attribute_record.description,
                'format_specification':json.loads(attribute_record.format_specification),
                'first_applicable_object':attribute_record.first_applicable_object}
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(str(attribute_id))
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    return HttpResponse(json.dumps(attribute_details))   


# used in query_data.html
@login_required
def get_data_points(request):

    request_body = json.loads(request.body)
    object_type_id = request_body['object_type_id']
    filter_facts = request_body['filter_facts']
    specified_start_time = int(request_body['specified_start_time'])
    specified_end_time = int(request_body['specified_end_time'])

    response = query_data.get_data_points(object_type_id, filter_facts, specified_start_time, specified_end_time)
    return HttpResponse(json.dumps(response))


# ==================
# FIND
# ==================


# used in: upload_data5
@login_required
def find_suggested_attributes(request):

    request_body = json.loads(request.body)
    attributenumber = request_body['attributenumber']
    object_type_id = request_body['object_type_id']
    column_values = request_body['column_values']

    response = []
    attributes = Attribute.objects.all()
    for attribute in attributes:
        format_specification = json.loads(attribute.format_specification)
        attribute_format = format_specification['fields']['column']
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name, 'description': attribute.description, 'format': attribute_format, 'comments': '{}'})
    return HttpResponse(json.dumps(response))


# used in: upload_data5 
# get_suggested_attributes2 get the concluding_format instead of just the attribute's format
@login_required
def find_suggested_attributes2(request):
    request_body = json.loads(request.body)
    attributenumber = request_body['attributenumber']
    object_type_id = request_body['object_type_id']
    upload_id = int(request_body['upload_id'])
    column_values = request_body['column_values']

    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]
    
    response = []
    attributes = Attribute.objects.all().filter(first_applicable_object__in=list_of_parent_object_ids)
    for attribute in attributes:
        concluding_format = get_from_db.get_attributes_concluding_format(attribute.id, object_type_id, upload_id)
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name, 'description': attribute.description, 'format': concluding_format['format_specification'], 'comments': concluding_format['comments']})
    return HttpResponse(json.dumps(response))


# used in: upload_data6 
@login_required
def find_matching_entities(request):
    request_body = json.loads(request.body)
    match_attributes = request_body['match_attributes']
    match_values = request_body['match_values']
    matching_objects_entire_list = []

    for row_nb in range(len(match_values[0])):
        matching_objects_dict = {}

        # append all matching datapoints
        found_datapoints = Data_point.objects.none()
        for attribute_nb, attribute_details in enumerate(match_attributes):

            additional_datapoints = Data_point.objects.filter(attribute_id=attribute_details['attribute_id'], attribute_value = json.dumps({'value':match_values[attribute_nb][row_nb]}))
            found_datapoints = found_datapoints.union(additional_datapoints)

        # get the object_ids  - those with most matching datapoints first
        object_id_list = found_datapoints.values('object_id').annotate(Count('object_id')).order_by('-object_id__count').values_list('object_id', flat=True)

        for object_id in object_id_list:
            # create a matching_object for each of the found object_id (containing the values from the this object_id)
            matching_object = {}
            for datapoint in found_datapoints.filter(object_id=object_id):
                matching_object[datapoint.attribute_id] = datapoint.attribute_value
            matching_objects_dict['object_id'] = matching_object
            
        
        matching_objects_entire_list.append(matching_objects_dict)

    return HttpResponse(json.dumps(matching_objects_entire_list))



# ==================
# SAVE
# ==================
@login_required
def save_new_object_hierachy_tree(request):
    if request.method == 'POST':
        new_entry = Object_hierachy_tree_history(object_hierachy_tree=request.body, user=request.user)
        new_entry.save()
        return HttpResponse("success")
    else:
        return HttpResponse("This must be a POST request.")


# used in: upload_data3 (the create-object-type modal)
@login_required
def save_new_object_type(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            object_facts = request_body['li_attr']['attribute_values']
            request_body['li_attr']['attribute_values'] = get_from_db.convert_fact_values_to_the_right_format(object_facts)
            new_entry = Object_types(id=request_body['id'], parent=request_body['parent'], name=request_body['text'], li_attr=json.dumps(request_body['li_attr']), a_attr=None)
            new_entry.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")


# used in: upload_data3 (the create-object-type modal)
@login_required
def save_edited_object_type(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            object_facts = request_body['li_attr']['attribute_values']
            request_body['li_attr']['attribute_values'] = get_from_db.convert_fact_values_to_the_right_format(object_facts)
            edited_object_type = Object_types.objects.get(id=request_body['id'])
            edited_object_type.parent = request_body['parent']
            edited_object_type.name = request_body['text']
            edited_object_type.li_attr = json.dumps(request_body['li_attr'])
            edited_object_type.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




# used in: upload_data3
@login_required
def save_edited_object_type(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            object_facts = request_body['li_attr']['attribute_values']
            request_body['li_attr']['attribute_values'] = get_from_db.convert_fact_values_to_the_right_format(object_facts)
            edited_object_type = Object_types.objects.get(id=request_body['id'])
            edited_object_type.parent = request_body['parent']
            edited_object_type.name = request_body['text']
            edited_object_type.li_attr = json.dumps(request_body['li_attr'])
            edited_object_type.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")

# used in: create_attribute_modal.html (i.e. upload_data3,4,5)
@login_required
def save_new_attribute(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)

            new_entry = Attribute(name=request_body['name'], data_type=request_body['data_type'], expected_valid_period=request_body['expected_valid_period'], description=request_body['description'], first_applicable_object=request_body['first_applicable_object'], format_specification=json.dumps(request_body['format_specification']))
            new_entry.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")


# used in: edit_attribute_modal.html (i.e. upload_data3,4,5)
@login_required
def save_changed_attribute(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            attribute_record = Attribute.objects.get(id=request_body['attribute_id'])

            attribute_record.name = request_body['name']
            attribute_record.data_type = request_body['data_type']
            attribute_record.expected_valid_period = request_body['expected_valid_period']
            attribute_record.description = request_body['description']
            attribute_record.first_applicable_object = request_body['first_applicable_object']
            attribute_record.format_specification = json.dumps(request_body['format_specification'])
            attribute_record.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")


# ==================
# DELETE
# ==================

# used in: upload_data3 (the create-object-type modal)
@login_required
def delete_object_type(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            object_id = request_body['object_id']

            delted_object = Object_types.objects.get(id=object_id)

            children_of_deleted_object  = Object_types.objects.filter(parent=object_id)
            for child in children_of_deleted_object:
                child.parent = delted_object.parent
                child.save()

            delted_object.delete()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




# used in: edit_attribute_modal.html
@login_required
def delete_attribute(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            attribute_id = request_body['attribute_id']

            attribute = Attribute.objects.get(id=attribute_id)
            attribute.delete()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")

# ==================
# PROCESS/EDIT
# ==================

@login_required
def edit_column(request): 
    request_body = json.loads(request.body)

    transformation = request_body['transformation']
    transformation = transformation.replace('"','')

    subset_specification = request_body['subset_specification']
    subset_specification = subset_specification.replace('"','')
    if subset_specification.replace(' ','') != "":
        subset_specification = subset_specification + " and "

    column = request_body['edited_column']
    # column = column.replace('"','')

    edited_column = column
    errors = []

    try:
        entire_code = "edited_column = [" + transformation + " if " + subset_specification + "value is not None else value for value in " + str(column) + " ]"
        execution_results = {}
        exec(entire_code, globals(), execution_results)
        edited_column = execution_results['edited_column']
    except Exception as error:
        traceback.print_exc()
        errors.append(str(error))

    response = {}
    response['errors'] = errors
    response['edited_column'] = edited_column
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(response['edited_column'])
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    return HttpResponse(json.dumps(response))


# ==================
# COLUMN FORMAT
# ==================

@login_required
def suggest_attribute_format(request): 
    request_body = json.loads(request.body)
    column_values = request_body['column_values']
    column_dict = {'column': column_values}
    constraints_dict = tdda_functions.suggest_attribute_format(column_dict)
    return HttpResponse(json.dumps(constraints_dict))



@login_required
def get_columns_format_violations(request):
    request_body = json.loads(request.body)
    attribute_id = request_body['attribute_id']
    column_values = request_body['column_values']

    violating_rows = tdda_functions.get_columns_format_violations(attribute_id, column_values)
    return HttpResponse(json.dumps(violating_rows))






def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False


@login_required
def check_single_fact_format(request):
    attribute_id = request.GET.get('attribute_id', '')
    operator = request.GET.get('operator', '')
    value = request.GET.get('value', '')

    response = {}
    response['fact_number'] = int(request.GET.get('fact_number', ''))

    if (attribute_id == '') or (value == '') or not is_int(attribute_id):
        response['format_violation_text'] = ''
        return HttpResponse(json.dumps(response))
        
    attribute_id = int(attribute_id)
    attribute_record = Attribute.objects.get(id=attribute_id)

    if attribute_record is None:
        response['format_violation_text'] = 'This attribute wasn''t found.'
        return HttpResponse(json.dumps(response))
    
    attribute_name = attribute_record.name
    format_specification = json.loads(attribute_record.format_specification)
    if (operator not in ['=', '>', '<', 'in']):
        response['format_violation_text'] = '"' + operator +'" is not a valid operator.'
        return HttpResponse(json.dumps(response))

    if (operator == 'in') and ('allowed_values' not in format_specification['fields']['column'].keys()):
        response['format_violation_text'] = 'The "in" operator is only permitted for categorical attributes.'
        return HttpResponse(json.dumps(response))
        
    if (operator in ['>', '<']) and (format_specification['fields']['column']['type'] not in ['int','real']):
        response['format_violation_text'] = 'The "<" and ">" operators are only permitted for attributes with type "real" or "int".'
        return HttpResponse(json.dumps(response))

    if format_specification['fields']['column']['type']=='int':
        if is_int(value):
            value = int(value)
        else:
            response['format_violation_text'] = attribute_name +'-values must be integers. ' + value + ' is not an integer.'
            return HttpResponse(json.dumps(response))

    if format_specification['fields']['column']['type']=='real':
        if is_float(value):
            value = float(value)
        else:
            response['format_violation_text'] = attribute_name +'-values must be real numbers. ' + value + ' is not a number.'
            return HttpResponse(json.dumps(response))

    if format_specification['fields']['column']['type']=='bool':
        if value.lower() in ['true', 'true ', 'tru', 't', 'yes', 'yes ', 'y']:
            value = True
        elif value.lower() in ['false', 'false ', 'flase', 'f', 'no', 'no ', 'n']:
            value = False
        else:
            response['format_violation_text'] = attribute_name +'-values must be "true" or "false", not ' + value + '.'
            return HttpResponse(json.dumps(response))

    violating_columns = tdda_functions.get_columns_format_violations(attribute_id, [value])
    if len(violating_columns) > 0:
        format_violation_text = 'The value "' + str(value) + '" does not satisfy the required format for ' + attribute_name + '-values. <br />'
        format_violation_text += 'It must satisfy: <ul>'
        for key in format_specification['fields']['column'].keys():
            format_violation_text += '<li>' + str(key) + ' = ' + str(format_specification['fields']['column'][key]) + '</li>'
        format_violation_text += '</ul>'
        response['format_violation_text'] = format_violation_text
        return HttpResponse(json.dumps(response))

    response['format_violation_text'] = ''
    return HttpResponse(json.dumps(response))

    


















 # ==========================================================================
 #   _____ _                 _       _   _             
 #  / ____(_)               | |     | | (_)            
 # | (___  _ _ __ ___  _   _| | __ _| |_ _  ___  _ __  
 #  \___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \ 
 #  ____) | | | | | | | |_| | | (_| | |_| | (_) | | | |
 # |_____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_|
 # 
 # ==========================================================================

@login_required
def query_data__simple(request):
    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tree_of_knowledge_frontend/query_data.html',{'object_hierachy_tree':object_hierachy_tree})


def download_file1(request):
    displayed_table_dict = json.loads(request.body)
    displayed_table_df = pd.DataFrame(displayed_table_dict)
    current_timestamp = int(round(time.time() * 1000))
    filename = str(current_timestamp) + ".csv"
    displayed_table_df.to_csv("collection/static/webservice files/downloaded_data_files/" + filename)
    return HttpResponse(current_timestamp)

def download_file2(request, file_name, file_type):
    # filename = request.GET.get('filename', '')
    displayed_table_df = pd.read_csv("collection/static/webservice files/downloaded_data_files/" + file_name + ".csv")
    column_names = displayed_table_df.columns
    
    if file_type=='xls':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="tree_of_knowledge_data.xls"'

        #creating workbook
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("sheet1")

        # headers
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        for column_number, column_name in enumerate(column_names[1:]):
            ws.write(0, column_number, column_name, font_style)

        # table body
        font_style.font.bold = False
        for index, row in displayed_table_df.iterrows():
            for column_number, value in enumerate(row.tolist()[1:]):
                ws.write(index + 1, column_number, value, font_style)

        wb.save(response)
        return response

    elif file_type=='csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tree_of_knowledge_data.csv"'

        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        # headers
        smart_str_column_names = [smart_str(name) for name in column_names[1:]]
        writer.writerow(smart_str_column_names)

        # table body
        for index, row in displayed_table_df.iterrows():
            smart_str_row = [smart_str(value) for value in row.tolist()[1:]]
            writer.writerow(smart_str_row)
            
        return response




def download_file2_csv(request):
    filename = request.GET.get('filename', '')
    displayed_table_dict = pd.read_csv("collection/static/webservice files/downloaded_data_files/" + filename + ".csv")
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(displayed_table_df.columns)
    for index, row in displayed_table_df.iterrows():
        writer.writerow(row.tolist())
    return response



@login_required
def edit_model(request, id):
    model = Simulation_model.objects.get(id=id)
    form_class = Simulation_modelForm
    form = form_class(data=request.POST, instance=model)

    if model.is_private and (model.user != request.user):
        raise Http404

    if request.method == 'POST':
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()

    return render(request, 'tree_of_knowledge_frontend/edit_model.html', {'model':model, 'form': form,})



@login_required
def new_model(request):
    
    if request.method == 'POST':
        form_class = Simulation_modelForm
        form = form_class(data=request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user

            model.save()
            return redirect('edit_model', id= model.id)

    form_class = Simulation_modelForm
    form = form_class()
    return render(request, 'tree_of_knowledge_frontend/edit_model.html', {'form': form,})






 # ==========================================================================
 #
 #              _           _         _____                      
 #     /\      | |         (_)       |  __ \                     
 #    /  \   __| |_ __ ___  _ _ __   | |__) |_ _  __ _  ___  ___ 
 #   / /\ \ / _` | '_ ` _ \| | '_ \  |  ___/ _` |/ _` |/ _ \/ __|
 #  / ____ \ (_| | | | | | | | | | | | |  | (_| | (_| |  __/\__ \
 # /_/    \_\__,_|_| |_| |_|_|_| |_| |_|   \__,_|\__, |\___||___/
 #                                                __/ |          
 #                                               |___/    
 # 
 # ==========================================================================


def newsletter_subscribers(request):
    newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
    return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})


def clear_database(request):
    populate_db.clear_object_types()
    populate_db.clear_attributes()
    return HttpResponse('done')

def populate_database(request):
    populate_db.populate_object_types()
    populate_db.populate_attributes()
    return HttpResponse('done')

def backup_database(request):
    success_for_object_types = populate_db.backup_object_types()
    success_for_attributes = populate_db.backup_attributes()

    if (success_for_object_types and success_for_attributes):
        return HttpResponse('success')
    else:
        return HttpResponse('An error occured')



def test_page1(request):
    # return render(request, 'tree_of_knowledge_frontend/test_page1.html')
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    #decide file name
    response['Content-Disposition'] = 'attachment; filename="ThePythonDjango.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet
    ws = wb.add_sheet("sheet1")



    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True


    #write column headers in sheet
    columns = ['2af','sdfg',234,52,6,'dfg']
    for column_number in range(len(columns)):
        ws.write(0, column_number, columns[column_number], font_style)

    # Sheet body, remaining rows
    # font_style = xlwt.XFStyle()

    # for index, row in displayed_table_df.iterrows():
    #     print(index)
    #     for column_number, value in enumerate(row.tolist()):
    #         ws.write(index + 1, column_number, value, font_style)
    #     # ws.write(row_number, 1, my_row.start_date_time, font_style)
    #     # ws.write(row_number, 2, my_row.end_date_time, font_style)
    #     # ws.write(row_number, 3, my_row.notes, font_style)

    wb.save(response)
    return response



def test_page2(request):
    # return render(request, 'tree_of_knowledge_frontend/test_page2.html')
    displayed_table_dict = json.loads(request.body)
    displayed_table_df = pd.DataFrame(displayed_table_dict)

    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    #decide file name
    response['Content-Disposition'] = 'attachment; filename="ThePythonDjango.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet
    ws = wb.add_sheet("sheet1")



    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True


    #write column headers in sheet
    columns = displayed_table_df.columns
    for column_number in range(len(columns)):
        ws.write(0, column_number, columns[column_number], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for index, row in displayed_table_df.iterrows():
        print(index)
        for column_number, value in enumerate(row.tolist()):
            ws.write(index + 1, column_number, value, font_style)
        # ws.write(row_number, 1, my_row.start_date_time, font_style)
        # ws.write(row_number, 2, my_row.end_date_time, font_style)
        # ws.write(row_number, 3, my_row.notes, font_style)

    wb.save(response)
    return response



def test_page3(request):
    # return render(request, 'tree_of_knowledge_frontend/test_page3.html')
    # response content type
    response = HttpResponse(content_type='text/csv')
    #decide the file name
    response['Content-Disposition'] = 'attachment; filename="ThePythonDjango.csv"'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    #write the headers
    writer.writerow([
        smart_str(u"Event Name"),
        smart_str(u"Start Date"),
        smart_str(u"End Date"),
        smart_str(u"Notes"),
    ])
    #get data from database or from text file....
    events = event_services.get_events_by_year(year) #dummy function to fetch data
    for event in events:
        writer.writerow([
            smart_str(event.name),
            smart_str(event.start_date_time),
            smart_str(event.end_date_time),
            smart_str(event.notes),
        ])
    return response
    