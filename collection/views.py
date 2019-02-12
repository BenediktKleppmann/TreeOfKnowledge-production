from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset, Object_hierachy_tree_history, Attribute, Object_types
from collection.forms import UserForm, ProfileForm, Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3, Uploaded_datasetForm4, Uploaded_datasetForm5, Uploaded_datasetForm6, Uploaded_datasetForm7
from django.template.defaultfilters import slugify
from collection.functions import upload_data, get_from_db, populate_db, tdda_functions
from django.http import HttpResponse
import json
import traceback


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
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form2.save()
            return redirect('upload_data3', upload_id=upload_id)

    known_data_sources = get_from_db.get_known_data_sources()
    return render(request, 'tree_of_knowledge_frontend/upload_data2.html', {'uploaded_dataset': uploaded_dataset, 'known_data_sources': known_data_sources, 'errors': errors})


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
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(json.dumps(object_hierachy_tree))
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
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

    print('uploaded_dataset.data_generation_date.year = ' + str(uploaded_dataset.data_generation_date.year))
    return render(request, 'tree_of_knowledge_frontend/upload_data4.html', {'uploaded_dataset': uploaded_dataset, 'data_generation_year':uploaded_dataset.data_generation_date.year, 'errors': errors})




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
            return redirect('upload_data6', upload_id=upload_id)
 
    return render(request, 'tree_of_knowledge_frontend/upload_data5.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def upload_data6(request, upload_id):
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
   
    return render(request, 'tree_of_knowledge_frontend/upload_data6.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})




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
            new_model_id = upload_data.perform_uploading(uploaded_dataset)
            return redirect('upload_data_success', new_model_id=new_model_id)
   
    return render(request, 'tree_of_knowledge_frontend/upload_data7.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})


@login_required
def upload_data_success(request, new_model_id):
    all_models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tree_of_knowledge_frontend/upload_data_success.html', {'new_model_id':new_model_id, 'all_models': all_models})



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
    print("object_type_id = %s" % request.GET.get('object_type_id', ''))
    response = []
    attributes = Attribute.objects.all()
    for attribute in attributes:
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name})
    return HttpResponse(json.dumps(response))


@login_required
def get_suggested_attributes(request):

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

# get_suggested_attributes2 get the concluding_format instead of just the attribute's format
@login_required
def get_suggested_attributes2(request):
    request_body = json.loads(request.body)
    attributenumber = request_body['attributenumber']
    object_type_id = request_body['object_type_id']
    upload_id = int(request_body['upload_id'])
    column_values = request_body['column_values']

    response = []
    attributes = Attribute.objects.all()
    for attribute in attributes:
        concluding_format = get_from_db.get_attributes_concluding_format(attribute.id, object_type_id, upload_id)
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name, 'description': attribute.description, 'format': concluding_format['format_specification'], 'comments': concluding_format['comments']})
    return HttpResponse(json.dumps(response))

@login_required
def get_list_of_parent_objects(request):
    object_type_id = request.GET.get('object_type_id', '')
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    return HttpResponse(json.dumps(list_of_parent_objects))


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

# used in: upload_data4
@login_required
def save_new_attribute(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)

            new_entry = Attribute(name=request_body['name'], description=request_body['description'], first_applicable_object=request_body['first_applicable_object'], format_specification=json.dumps(request_body['format_specification']))
            new_entry.save()
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

    column = request_body['edited_column']
    # column = column.replace('"','')

    edited_column = column
    errors = []

    try:
        entire_code = "edited_column = [" + transformation + " for value in " + str(column) + "]"
        execution_results = {}
        exec(entire_code, globals(), execution_results)
        
        edited_column = execution_results['edited_column']
    except Exception as error:
        traceback.print_exc()
        errors.append(str(error))

    response = {}
    response['errors'] = errors
    response['edited_column'] = edited_column
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
    populate_db.clear_object_hierachy_tree()
    populate_db.clear_attributes()
    return HttpResponse('done')

def populate_database(request):
    populate_db.populate_object_hierachy_tree()
    populate_db.populate_attributes()
    return HttpResponse('done')



def test_page1(request):
    return render(request, 'tree_of_knowledge_frontend/test_page1.html')

def test_page2(request):
    return HttpResponse(str(request.user.profile.verbose))

def test_page3(request):
    return render(request, 'tree_of_knowledge_frontend/test_page3.html')
    # populate_db.clear_attributes()
    # populate_db.populate_attributes()

    # attributes = Attribute.objects.all()
    # response = {}
    
    # for att_nb, attribute in enumerate(attributes):
    #     # response[attribute.name] = "hello"
    #     attribute_dict = {}
    #     attribute_dict['description'] = attribute.description
    #     attribute_dict['format_specification'] = attribute.format_specification
    #     attribute_dict['first_applicable_object'] = attribute.first_applicable_object.id
    #     response[attribute.name] = attribute_dict
    # return HttpResponse("success")
    





