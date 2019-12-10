from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset, Object_hierachy_tree_history, Attribute, Object_types, Data_point, Object, Calculation_rule, Learned_rule, Rule, Likelihood_fuction
from django.db.models import Count
from collection.forms import UserForm, ProfileForm, Subscriber_preferencesForm, Subscriber_registrationForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3, Uploaded_datasetForm4, Uploaded_datasetForm5, Uploaded_datasetForm6, Uploaded_datasetForm7
from django.template.defaultfilters import slugify
from collection.functions import upload_data, get_from_db, admin_fuctions, tdda_functions, query_datapoints, simulation
from django.http import HttpResponse
import json
import traceback
import csv
import pandas as pd
import xlwt
from django.utils.encoding import smart_str
import time
import os
from django.views.decorators.csrf import csrf_protect, csrf_exempt, requires_csrf_token
import numpy as np
import math
from scipy.stats import beta
import scipy
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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
            first_name = form.cleaned_data['first_name']
            subscriber = Newsletter_subscriber.objects.get(email=email)

            message = '''Hi ''' + first_name + ''',

            Thank you for subscribing to the Tree of Knowledge newsletter.
            '''
            email_message = EmailMultiAlternatives('Tree of Knowledge Newsletter', message, 'noreply@treeofknowledge.ai', [email])
            email_message.send()
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
    simulation_models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tool/main_menu.html', {'simulation_models': simulation_models})


@login_required
def open_your_simulation(request):
    simulation_models = Simulation_model.objects.filter(user=request.user).order_by('-id') 
    return render(request, 'tool/open_your_simulation.html', {'simulation_models': simulation_models})

@login_required
def browse_simulations(request):
    simulation_models = Simulation_model.objects.all().order_by('-id') 
    return render(request, 'tool/browse_simulations.html', {'simulation_models': simulation_models})


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
   
    return render(request, 'tool/profile_and_settings.html', {'errors': errors})



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
    print('upload_data1_new')
    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                print('save_new_upload_details')
                (upload_id, upload_error, new_errors) = upload_data.save_new_upload_details(request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tool/upload_data1.html', {'upload_error':upload_error, 'errors': errors})
                else:
                    return redirect('upload_data1', upload_id=upload_id)

        return render(request, 'tool/upload_data1.html', {'errors': errors})
        # return redirect('upload_data1', upload_id=upload_id, errors=errors)
    else:
        return render(request, 'tool/upload_data1.html', {'errors': errors})



@login_required
def upload_data1(request, upload_id, errors=[]):
    print('upload_data1')
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'errors': errors})

    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            if data_file.name[-4:] !=".csv":
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                print('save_existing_upload_details')
                (upload_error, new_errors) = upload_data.save_existing_upload_details(upload_id, request)
                if upload_error:
                    errors.extend(new_errors)
                    return render(request, 'tool/upload_data1.html', {'upload_error':upload_error, 'errors': errors, 'uploaded_dataset':uploaded_dataset})
                else:
                    return redirect('upload_data1', upload_id=upload_id)


    return render(request, 'tool/upload_data1.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})




@login_required
def upload_data2(request, upload_id):
    errors = []
    error_dict = '{}'
    
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    if request.method == 'POST':
        form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
            error_dict = json.dumps(dict(form2.errors))
        else:
            form2.save()
            return redirect('upload_data3', upload_id=upload_id)

    known_data_sources = get_from_db.get_known_data_sources()
    return render(request, 'tool/upload_data2.html', {'upload_id': upload_id, 'uploaded_dataset': uploaded_dataset, 'known_data_sources': known_data_sources, 'errors': errors, 'error_dict': error_dict})


@login_required
def upload_data3(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    
    if request.method == 'POST':
        print('******************************************************')
        print(json.dumps(request.POST))
        print('******************************************************')
        form3 = Uploaded_datasetForm3(data=request.POST, instance=uploaded_dataset)
        if not form3.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form3.save()
            return redirect('upload_data4', upload_id=upload_id)

    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tool/upload_data3.html', {'upload_id': upload_id, 'uploaded_dataset': uploaded_dataset, 'object_hierachy_tree':object_hierachy_tree, 'errors': errors})


@login_required
def upload_data4(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    
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
    return render(request, 'tool/upload_data4.html', {'upload_id': upload_id, 'uploaded_dataset': uploaded_dataset, 'data_generation_year':data_generation_year, 'errors': errors})




@login_required
def upload_data5(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})
    
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
 
    return render(request, 'tool/upload_data5.html', {'upload_id': upload_id, 'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def upload_data6A(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    if request.method == 'POST':
        form6 = Uploaded_datasetForm6(data=request.POST, instance=uploaded_dataset)
        if not form6.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form6.save()
            if uploaded_dataset.data_generation_date is None:
                return redirect('upload_data7', upload_id=upload_id)
            else:
                (number_of_datapoints_saved, new_model_id) = upload_data.perform_uploading(uploaded_dataset, request)
                return redirect('upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
   
    table_attributes = upload_data.make_table_attributes_dict(uploaded_dataset)
    return render(request, 'tool/upload_data6.html', {'upload_id': upload_id, 'data_table_json': uploaded_dataset.data_table_json, 'table_attributes': table_attributes, 'errors': errors})



@login_required
def upload_data6B(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    if request.method == 'POST':
        form6 = Uploaded_datasetForm6(data=request.POST, instance=uploaded_dataset)
        print(request.POST.get('list_of_matches', None))
        print(request.POST.get('upload_only_matched_entities', None))
        
        if not form6.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form6.save()
            (number_of_datapoints_saved, new_model_id) = upload_data.perform_uploading_for_timeseries(uploaded_dataset, request)
            if 'DB_CONNECTION_URL' in os.environ:
                return redirect('https://www.treeofknowledge.ai/tool/upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
            else:
                return redirect('upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
   
    
    table_attributes = upload_data.make_table_attributes_dict(uploaded_dataset)
    if uploaded_dataset.object_identifiers is None:
        data_table_json = uploaded_dataset.data_table_json
    else: 
        data_table_json_dict = upload_data.make_data_table_json_with_distinct_entities(uploaded_dataset)
        data_table_json = json.dumps(data_table_json_dict)
    return render(request, 'tool/upload_data6.html', {'upload_id': upload_id, 'data_table_json': data_table_json, 'table_attributes': table_attributes, 'errors': errors})




@login_required
def upload_data7(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        return render(request, 'tool/upload_data1.html', {'upload_id': upload_id, 'errors': errors})

    
    if request.method == 'POST':
        form7 = Uploaded_datasetForm7(data=request.POST, instance=uploaded_dataset)
        if not form7.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form7.save()
            (number_of_datapoints_saved, new_model_id) = upload_data.perform_uploading(uploaded_dataset, request)
            if 'DB_CONNECTION_URL' in os.environ:
                return redirect('https://www.treeofknowledge.ai/tool/upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
            else:
                return redirect('upload_data_success', number_of_datapoints_saved=number_of_datapoints_saved, new_model_id=new_model_id)
   
    return render(request, 'tool/upload_data7.html', {'upload_id': upload_id, 'uploaded_dataset': uploaded_dataset, 'errors': errors})


@login_required
def upload_data_success(request, number_of_datapoints_saved, new_model_id):
    all_simulation_models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tool/upload_data_success.html', {'number_of_datapoints_saved':number_of_datapoints_saved, 'new_model_id':new_model_id, 'all_simulation_models': all_simulation_models})



@login_required
def get_upload_progress(request):
    upload_id = request.GET.get('upload_id', '')

    with open('collection/static/webservice files/runtime_data/upload_progress_' + upload_id + '.txt') as file:       
        progress = file.readline().strip()

    return HttpResponse(progress)



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
# simple GET
# ==================


@login_required
def get_possible_attributes(request):
    object_type_id = request.GET.get('object_type_id', '')
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]



    response = []
    attributes = Attribute.objects.all().filter(first_applicable_object_type__in=list_of_parent_object_ids)
    
    for attribute in attributes:
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name, 'attribute_data_type': attribute.data_type, 'attribute_first_relation_object_type': attribute.first_relation_object_type})
    return HttpResponse(json.dumps(response))

# used in create_attribute_modal.html
@login_required
def get_list_of_parent_objects(request):
    object_type_id = request.GET.get('object_type_id', '')
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    print('___________________________________________________________')
    print(object_type_id)
    print(list_of_parent_objects)
    print('___________________________________________________________')
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
				'first_applicable_object_type':attribute_record.first_applicable_object_type,
                'first_relation_object_type':attribute_record.first_relation_object_type}
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(str(attribute_id))
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    return HttpResponse(json.dumps(attribute_details))   


# used in edit_model.html
@login_required
def get_attribute_rules_old(request):
    attribute_id = request.GET.get('attribute_id', '')
    attribute_id = int(attribute_id)
    rule_records = Calculation_rule.objects.filter(attribute_id=attribute_id).order_by('-number_of_times_used')
    rules_list = list(rule_records.values())
    return HttpResponse(json.dumps(rules_list)) 



@login_required
def get_object_hierachy_tree(request):
    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return HttpResponse(object_hierachy_tree)


@login_required
def get_available_variables(request):
    object_type_id = request.GET.get('object_type_id', '')
    available_variables = []
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    for parent_object in list_of_parent_objects:
        available_variables.extend(list(Attribute.objects.filter(first_applicable_object_type=parent_object['id']).values('name', 'id', 'data_type')))
    return HttpResponse(json.dumps(available_variables))
    


# used in edit_model.html
@login_required
def get_object_rules(request):
    object_type_id = request.GET.get('object_type_id', '')

    response = {}
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    parent_object_type_ids = [obj['id'] for obj in list_of_parent_objects]
    attributes = Attribute.objects.filter(first_applicable_object_type__in=parent_object_type_ids).values()
    for attribute in attributes:
        response[attribute['id']] = {'used_rules': {},
                                    'not_used_rules':{},
                                    'execution_order':[]}
        rules_list = list(Rule.objects.filter(changed_var_attribute_id=attribute['id']).values())
        for rule in rules_list:

            # calculate 'probability' and 'standard_dev'
            histogram, mean, standard_dev = get_from_db.get_rules_pdf(rule['id'])
            rule['probability'] = mean
            rule['standard_dev'] = standard_dev

            # specify a default for 'learn_posterior'
            rule['learn_posterior'] = False
            if not rule['has_probability_1'] and rule['probability'] is None:
                rule['learn_posterior'] = True

            response[attribute['id']]['used_rules'][rule['id']] = rule
            response[attribute['id']]['execution_order'].append(rule['id'])
    return HttpResponse(json.dumps(response)) 


# used in edit_object_behaviour_modal.html (which in turn is used in edit_simulation.html and analyse_simulation.html)
@login_required
def get_rules_pdf(request):
    rule_id = request.GET.get('rule_id', '')
    histogram, mean, standard_dev = get_from_db.get_rules_pdf(rule_id)
    
    smooth_pdf = True
    if smooth_pdf:
        hist_dist = scipy.stats.rv_histogram(histogram)
        hist_sample = hist_dist.rvs(size=10000)
        a, b, min_value, value_range = beta.fit(hist_sample) 
        x_values = list(histogram[1])[:-1]
        pdf_values = [beta.pdf(x,a,b) for x in x_values]
        response = [[x, prob] for x, prob in zip(x_values, pdf_values)]
    else:
        response = [[bucket_value, count] for bucket_value, count in zip(histogram[1], histogram[0])]
    return HttpResponse(json.dumps(response))


# used in edit_object_behaviour_modal.html (which in turn is used in edit_simulation.html and analyse_simulation.html)
@login_required
def get_single_pdf(request):
    response = {}
    simulation_id = request.GET.get('simulation_id', '')
    object_number = request.GET.get('object_number', '')
    rule_id = request.GET.get('rule_id', '')
    histogram, mean, standard_dev, message = get_from_db.get_single_pdf(simulation_id, object_number, rule_id)

    if message != '':
        response['message'] = message

    smooth_pdf = True
    if smooth_pdf:
        print(histogram)
        hist_dist = scipy.stats.rv_histogram(histogram)
        hist_sample = hist_dist.rvs(size=10000)
        a, b, min_value, value_range = beta.fit(hist_sample) 
        x_values = list(histogram[1])[:-1]
        pdf_values = [beta.pdf(x,a,b) for x in x_values]
        pdf_values = np.minimum(pdf_values, 100)
        response['pdf'] = [[x, prob] for x, prob in zip(x_values, pdf_values)]
    else:
        response['pdf'] = [[bucket_value, count] for bucket_value, count in zip(histogram[1], histogram[0])]
    return HttpResponse(json.dumps(response))
    

# ==================
# complex GET
# ==================

# used in query_data.html
@login_required
def get_data_points(request):
    request_body = json.loads(request.body)
    object_type_id = request_body['object_type_id']
    filter_facts = request_body['filter_facts']
    specified_start_time = int(request_body['specified_start_time'])
    specified_end_time = int(request_body['specified_end_time'])

    response = query_datapoints.get_data_points(object_type_id, filter_facts, specified_start_time, specified_end_time)
    return HttpResponse(json.dumps(response))


# used in edit_model.html
@login_required
def get_data_from_random_object(request):
    request_body = json.loads(request.body)
    object_number = request_body['object_number']
    object_type_id = request_body['object_type_id']
    filter_facts = request_body['filter_facts']
    specified_start_time = request_body['specified_start_time']
    specified_end_time = request_body['specified_end_time']

    (object_id, attribute_values) = query_datapoints.get_data_from_random_object(object_type_id, filter_facts, specified_start_time, specified_end_time)
    response = {'object_number':object_number, 'object_id':object_id, 'attribute_values':attribute_values}
    return HttpResponse(json.dumps(response))


# used in edit_model.html
@login_required
def get_data_from_random_related_object(request):
    request_body = json.loads(request.body)
    objects_dict = request_body['objects_dict']
    specified_start_time = request_body['specified_start_time']
    specified_end_time = request_body['specified_end_time']

    all_attribute_values = query_datapoints.get_data_from_random_related_object(objects_dict, specified_start_time, specified_end_time)
    return HttpResponse(json.dumps(all_attribute_values))


# used in query_data.html
@login_required
def get_data_from_objects_behind_the_relation(request):
    request_body = json.loads(request.body)
    object_type_id = request_body['object_type_id']
    object_ids = request_body['object_ids']
    specified_start_time = request_body['specified_start_time']
    specified_end_time = request_body['specified_end_time']
    print('*******************************************************')
    print(request_body.keys())
    print(request_body['object_type_id'])
    print(request_body['object_ids'])
    print(request_body['specified_start_time'])
    print(request_body['specified_end_time'])
    print('*******************************************************')

    response = query_datapoints.get_data_from_objects_behind_the_relation(object_type_id, object_ids, specified_start_time, specified_end_time)   
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
    print('find_suggested_attributes2')
    request_body = json.loads(request.body)
    attributenumber = request_body['attributenumber']
    object_type_id = request_body['object_type_id']
    upload_id = int(request_body['upload_id'])
    column_values = request_body['column_values']
    print('1')

    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]
  
    print('2')
    response = []
    attributes = Attribute.objects.all().filter(first_applicable_object_type__in=list_of_parent_object_ids)

    print('3')
    for attribute in attributes:
        print('4')
        concluding_format = get_from_db.get_attributes_concluding_format(attribute.id, object_type_id, upload_id)
        print('5')
        response.append({'attribute_id': attribute.id, 'attribute_name': attribute.name, 'description': attribute.description, 'format': concluding_format['format_specification'], 'comments': concluding_format['comments'], 'data_type': attribute.data_type, 'object_type_id_of_related_object': attribute.first_relation_object_type})

    print('6')
    return HttpResponse(json.dumps(response))


# used in: upload_data6 
@login_required
def find_matching_entities(request):
    request_body = json.loads(request.body)
    match_attributes = request_body['match_attributes']
    match_values = request_body['match_values']
    matching_objects_entire_list_string = query_datapoints.find_matching_entities(match_attributes, match_values)
    print(matching_objects_entire_list_string)
    print(type(matching_objects_entire_list_string))
    return HttpResponse(matching_objects_entire_list_string)


# used in: additional_facts_functions.html, which in turn is used in upload_data3 and upload_data4
# this function should be extended to also find fuzzy matches and suggest them in the format_violation_text
@login_required
def find_single_entity(request):
    relation_id = request.GET.get('relation_id', '')
    print('++++++++ ' + relation_id + ' +++++++++++++++++')
    attribute_id = request.GET.get('attribute_id', '')
    value = request.GET.get('value', '')

    matching_object_id = query_datapoints.find_single_entity(relation_id, attribute_id, value)
    response = {'fact_number': int(request.GET.get('fact_number', '')),
                'matching_object_id':matching_object_id}
    return HttpResponse(json.dumps(response))


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
            new_entry = Object_types(id=request_body['id'], parent=request_body['parent'], name=request_body['text'], li_attr=json.dumps(request_body['li_attr']), a_attr=None, object_type_icon="si-glyph-square-dashed-2")
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




# used in: create_attribute_modal.html (i.e. upload_data3,4,5)
@login_required
def save_new_attribute(request):
    print('1')
    if request.method == 'POST':
        print('2')
        try:
            print('3')
            request_body = json.loads(request.body)

            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(request_body)
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            new_entry = Attribute(name=request_body['name'], 
                                data_type=request_body['data_type'], 
                                expected_valid_period=request_body['expected_valid_period'], 
                                description=request_body['description'], 
                                format_specification=json.dumps(request_body['format_specification']),
                                first_applicable_object_type=request_body['first_applicable_object_type'],
                                first_relation_object_type=request_body['first_relation_object_type'])
            print('4')
            new_entry.save()
            print('5')
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
            attribute_record.first_applicable_object_type = request_body['first_applicable_object_type']
            attribute_record.format_specification = json.dumps(request_body['format_specification'])
            attribute_record.save()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




@login_required
def save_rule(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            rule_id = request_body['id']


            if (rule_id is not None):
                rule_record = Rule.objects.get(id=rule_id)
                rule_record.changed_var_attribute_id = request_body['changed_var_attribute_id']
                rule_record.changed_var_data_type = request_body['changed_var_data_type']
                rule_record.condition_text = request_body['condition_text']
                rule_record.condition_exec = request_body['condition_exec']
                rule_record.effect_text = request_body['effect_text']
                rule_record.effect_exec = request_body['effect_exec']
                rule_record.effect_is_calculation = request_body['effect_is_calculation']
                rule_record.used_attribute_ids = request_body['used_attribute_ids']
                rule_record.is_conditionless = request_body['is_conditionless']
                rule_record.has_probability_1 = request_body['has_probability_1']
                rule_record.save()

            else:
                new_entry = Rule(changed_var_attribute_id= request_body['changed_var_attribute_id'],
                                changed_var_data_type= request_body['changed_var_data_type'],
                                condition_text= request_body['condition_text'],
                                condition_exec= request_body['condition_exec'],
                                effect_text= request_body['effect_text'],
                                effect_exec= request_body['effect_exec'],
                                effect_is_calculation= request_body['effect_is_calculation'],
                                used_attribute_ids= request_body['used_attribute_ids'],
                                is_conditionless= request_body['is_conditionless'],
                                has_probability_1= request_body['has_probability_1'])

                new_entry.save()

                rule_id = new_entry.id

            return HttpResponse(rule_id)
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




# used in: edit_model.html  and edit_model__simulate.html
@login_required
def save_changed_simulation(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            model_record = Simulation_model.objects.get(id=request_body['simulation_id'])
            model_record.is_timeseries_analysis = request_body['is_timeseries_analysis']
            model_record.objects_dict = json.dumps(request_body['objects_dict'])
            model_record.y_value_attributes = json.dumps(request_body['y_value_attributes'])
            model_record.object_type_counts = json.dumps(request_body['object_type_counts'])
            model_record.total_object_count = request_body['total_object_count']
            model_record.number_of_additional_object_facts = request_body['number_of_additional_object_facts']
            model_record.simulation_start_time = request_body['simulation_start_time']
            model_record.simulation_end_time = request_body['simulation_end_time']
            model_record.timestep_size = request_body['timestep_size']
            # model_record.selected_attribute = request_body['selected_attribute']
            model_record.save()

            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




# used in: learn_rule.html
# @login_required
# def save_learned_rule(request):
#     if request.method == 'POST':
#         try:
#             request_body = json.loads(request.body)

#             learned_rule_record = Learned_rule.objects.get(id=request_body['learned_rule_id'])
#             learned_rule_record.object_type_id = request_body['object_type_id']
#             learned_rule_record.object_filter_facts = json.dumps(request_body['object_filter_facts'])
#             learned_rule_record.specified_factors = json.dumps(request_body['specified_factors'])
#             learned_rule_record.save()

#             return HttpResponse("success")
#         except Exception as error:
#             traceback.print_exc()
#             return HttpResponse(str(error))
#     else:
#         return HttpResponse("This must be a POST request.")


# used in: learn_rule.html
@login_required
def save_changed_object_type_icon(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)

            object_type = Object_types.objects.get(id=request_body['object_type_id'])
            object_type.object_type_icon = request_body['object_type_icon']
            object_type.save()

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


# used in: edit_simulation__simulate.html
@login_required
def delete_rule(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            rule_id = request_body['rule_id']
            print('[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')
            print(rule_id)
            print('[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')

            rule = Rule.objects.get(id=rule_id)
            rule.delete()
            return HttpResponse("success")
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")

# ==================
# PROCESS
# ==================

# used in upload_data5.html
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

    return HttpResponse(json.dumps(response))



# used in learn_rule.html
# @login_required
# def learn_rule_from_factors(request):
#     learned_rule_id = int(request.GET.get('learned_rule_id', 0))
#     the_rule_learner = rule_learner.Rule_Learner(learned_rule_id)
#     response = the_rule_learner.run()

#     return HttpResponse(json.dumps(response))



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

    # if (operator == 'in') and ('allowed_values' not in format_specification['fields']['column'].keys()):
    #     response['format_violation_text'] = 'The "in" operator is only permitted for categorical attributes.'
    #     return HttpResponse(json.dumps(response))
        
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

    








 # ===============================================================
 #   ____                          _____        _        
 #  / __ \                        |  __ \      | |       
 # | |  | |_   _  ___ _ __ _   _  | |  | | __ _| |_ __ _ 
 # | |  | | | | |/ _ \ '__| | | | | |  | |/ _` | __/ _` |
 # | |__| | |_| |  __/ |  | |_| | | |__| | (_| | || (_| |
 #  \___\_\\__,_|\___|_|   \__, | |_____/ \__,_|\__\__,_|
 #                          __/ |                        
 #                         |___/                         
 # ===============================================================



@login_required
def query_data(request):
    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tool/query_data.html',{'object_hierachy_tree':object_hierachy_tree})


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
def edit_simulation_new(request):    
    simulation_model = Simulation_model(user=request.user, 
                                        is_timeseries_analysis=True,
                                        objects_dict=json.dumps({}), 
                                        y_value_attributes=json.dumps([]), 
                                        object_type_counts=json.dumps({}),
                                        total_object_count=0,
                                        number_of_additional_object_facts=2,
                                        simulation_start_time=946684800, 
                                        simulation_end_time=1577836800, 
                                        timestep_size=31536000)
    simulation_model.save()
    new_simulation_id = simulation_model.id
    return redirect('edit_simulation', simulation_id=new_simulation_id)



@login_required
def edit_simulation(request, simulation_id):
    simulation_model = Simulation_model.objects.get(id=simulation_id)

    if request.method == 'POST':
        the_simulator = simulation.Simulator(simulation_id)
        the_simulator.run()
        print('simulation completed, redirecting..')
        if 'DB_CONNECTION_URL' in os.environ:
            return redirect('https://www.treeofknowledge.ai/tool/analyse_simulation', simulation_id=simulation_id)
        else:
            return redirect('analyse_simulation', simulation_id=simulation_id)


    
    available_object_types = get_from_db.get_most_common_object_types()
    object_icons = [icon_name[:-4] for icon_name in os.listdir("collection/static/images/object_icons/")]
    available_relations = get_from_db.get_available_relations()
    return render(request, 'tool/edit_simulation.html', {'simulation_model':simulation_model, 'available_object_types': available_object_types, 'object_icons': object_icons, 'available_relations':available_relations})




@login_required
def get_simulation_progress(request):
    simulation_id = request.GET.get('simulation_id', '')

    with open('collection/static/webservice files/runtime_data/simulation_progress_' + simulation_id + '.txt') as file:       
        progress = file.readline()

    return HttpResponse(progress)




@login_required
def analyse_simulation(request, simulation_id):
    print('analyse_simulation')
   
    if request.method == 'POST':
        the_simulator = simulation.Simulator(simulation_id)
        the_simulator.run()
        simulation_model = Simulation_model.objects.get(id=simulation_id)
        return render(request, 'tool/analyse_simulation.html', {'simulation_model':simulation_model})


    with open('collection/static/webservice files/runtime_data/simulation_progress_' + str(simulation_id) + '.txt', "w") as progress_tracking_file:
        progress_tracking_file.write(json.dumps({"learning_likelihoods": False, "nb_of_accepted_simulations_total": "", "nb_of_accepted_simulations_current": "" , "running_monte_carlo": False, "monte_carlo__simulation_number": "", "monte_carlo__number_of_simulations":  "",}))
    simulation_model = Simulation_model.objects.get(id=simulation_id)
    return render(request, 'tool/analyse_simulation.html', {'simulation_model':simulation_model})




# @login_required
# def setup_rule_learning(request, simulation_id):

#     simulation_model = Simulation_model.objects.get(id=simulation_id)
#     objects_dict = json.loads(simulation_model.objects_dict)

#     object_number = int(request.POST.get('object_number', None))
#     attribute_id = int(request.POST.get('attribute_id', None))

#     valid_times = []
#     times = np.arange(simulation_model.simulation_start_time + simulation_model.timestep_size, simulation_model.simulation_end_time, simulation_model.timestep_size)
#     for index in range(len(times)-1):
#         valid_times.append([int(times[index]), int(times[index + 1])])

#     learned_rule = Learned_rule(object_type_id=objects_dict[str(object_number)]['object_type_id'], 
#                                 object_type_name=objects_dict[str(object_number)]['object_type_name'],
#                                 attribute_id=attribute_id,
#                                 attribute_name=objects_dict[str(object_number)]['object_attributes'][str(attribute_id)]['attribute_name'],
#                                 object_filter_facts=json.dumps(objects_dict[str(object_number)]['object_filter_facts']),
#                                 specified_factors = json.dumps({}),
#                                 sorted_factor_numbers = json.dumps([]),
#                                 valid_times= json.dumps(valid_times),
#                                 min_score_contribution = 0.01,
#                                 max_p_value = 0.05,
#                                 user=request.user)

#     learned_rule.save()
#     learned_rule_id = learned_rule.id



#     return redirect('learn_rule', learned_rule_id=learned_rule_id)



# @login_required
# def learn_rule(request, learned_rule_id):
#     learned_rule = Learned_rule.objects.get(id=learned_rule_id)

#     available_attributes = []
#     list_of_parent_objects = get_from_db.get_list_of_parent_objects(learned_rule.object_type_id)
#     for parent_object in list_of_parent_objects:
#         available_attributes.extend(list(Attribute.objects.filter(first_applicable_object_type=parent_object['id']).values('name', 'id', 'data_type')))

#     return render(request, 'tool/learn_rule.html', {'learned_rule':learned_rule, 'available_attributes': available_attributes})




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

@staff_member_required
def newsletter_subscribers(request):
    newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
    return render(request, 'admin_pages/newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})


@staff_member_required
def clear_database(request):
    admin_fuctions.clear_object_types()
    admin_fuctions.clear_attributes()
    return HttpResponse('done')


@staff_member_required
def populate_database(request):
    admin_fuctions.populate_object_types()
    admin_fuctions.populate_attributes()
    return HttpResponse('done')


@staff_member_required
def backup_database(request):
    success_for_object_types = admin_fuctions.backup_object_types()
    success_for_attributes = admin_fuctions.backup_attributes()

    if (success_for_object_types and success_for_attributes):
        return HttpResponse('success')
    else:
        return HttpResponse('An error occured')


@staff_member_required
def remove_duplicate_datapoints(request):
    admin_fuctions.remove_duplicates()
    return HttpResponse('success')


@staff_member_required
def find_possibly_duplicate_objects(request):
    possibly_duplicate_objects = admin_fuctions.find_possibly_duplicate_objects()
    object_types = list(Object_types.objects.all().values())
    object_types_names = {str(object_type['id']):object_type['name'] for object_type in object_types}
    return render(request, 'admin_pages/find_possibly_duplicate_objects.html', {'possibly_duplicate_objects': possibly_duplicate_objects, 'object_types_names':object_types_names})




@staff_member_required
def inspect_object(request, object_id):
    return render(request, 'admin_pages/inspect_object.html', {'object_id': object_id})

@staff_member_required
def get_object(request):
    object_id = request.GET.get('object_id', '')
    individual_object = admin_fuctions.inspect_individual_object(object_id)
    return HttpResponse(json.dumps(individual_object))



@staff_member_required
def inspect_upload(request, upload_id):
    return render(request, 'admin_pages/inspect_upload.html', {'upload_id': upload_id})

@staff_member_required
def get_uploaded_dataset(request):
    upload_id = request.GET.get('upload_id', None)
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id)
    uploaded_dataset_dict = {   'data_table_json':json.loads(uploaded_dataset.data_table_json),
                                'data_source':uploaded_dataset.data_source,
                                'data_generation_date':uploaded_dataset.data_generation_date.strftime('%Y-%m-%d %H:%M'),
                                'correctness_of_data':uploaded_dataset.correctness_of_data,
                                'object_type_name':uploaded_dataset.object_type_name,
                                'meta_data_facts':uploaded_dataset.meta_data_facts}

    return HttpResponse(json.dumps(uploaded_dataset_dict))



@staff_member_required
def upload_file(request):
    errors = []
    if request.method == 'POST':
        form1 = UploadFileForm(request.POST, request.FILES)
        if not form1.is_valid():
            errors.append("Error: Form not valid.")
        else:
            data_file = request.FILES['file']
            print(os.getcwd())
            with open('collection/static/webservice files/db_backup/' + data_file.name, 'wb+') as destination:
                for chunk in data_file.chunks():
                    destination.write(chunk)

            request.FILES['file']
            errors.append("The file was successfully uploaded.")

    return render(request, 'admin_pages/upload_file.html', {'errors': errors})



def test_page1(request):

    message = '''Hi ''' + user.username + ''',

Thank you for signing up to the Tree of Knowledge.'''
    email_message = EmailMultiAlternatives('Tree of Knowledge Newsletter', message, 'noreply@treeofknowledge.ai', ['benedikt@kleppmann.de'])
    email_message.send()


    # object_type_id = "j1_12"
    # filter_facts = []
    # specified_start_time = 946684800
    # specified_end_time = 1577836800
    # response = query_datapoints.get_data_points(object_type_id, filter_facts, specified_start_time, specified_end_time)
    # attributes = list(Attribute.objects.all().values())
    # list_of_child_objects = get_from_db.get_list_of_child_objects("j1_5")
    return HttpResponse("success")
    # return render(request, 'tool/test_page1.html')



def test_page2(request):
    # return render(request, 'tool/test_page2.html')
    # bla = list(Object.objects.filter(object_type_id__in=['j1_5']).values_list('id'))
    # bla = Uploaded_dataset.objects.get(id=94).data_table_json
    bla = list(Data_point.objects.filter(valid_time_start__gte=-1262307600, valid_time_start__lt=1577836800, object_id__in=[10930,10931,10932,10933,10934,10935,10936,10937,10938,10939,10940,10941,10942,10943,10944,10945,10946,10947,10948,10949,10950,10951,10952,10953,10954,10955,10956,10957,10958,10959,10960,10961,10962,10963,10964,10965,10966,10967,10968,10969,10970,10971,10972,10973,10974,10975,10976,10977,10978,10979,10980,10981,10982,10983,10984,10985,10986,10987,10988,10989,10990,10991,10992,10993,10994,10995,10996,10997,10998,10999,11000,11001,11002,11003,11004,11005,11006,11007,11008,11009,11010,11011,11012,11013,11014,11015,11016,11017,11018,11019,11020,11021,11022,11023,11024,11025,11026,11027,11028,11029,11030,11031,11032,11033,11034,11035,11036,11037,11038,11039,11040,11041,11042,11043,11044,11045,11046,11047,11048,11049,11050,11051,11052,11053,11054,11055,11056,11057,11058,11059,11060,11061,11062,11063,11064,11065,11066,11067,11068,11069,11070,11071,11072,11073,11074,11075,11076,11077,11078,11079]).values() )

    # return HttpResponse('success')
    return HttpResponse(json.dumps(bla))

    


def test_page3(request):
    current_object_type = list(Data_point.objects.filter(valid_time_start__gte=-1262307600, valid_time_start__lt=1577836800, object_id__in=[10930, 10931, 10932, 10933, 10934, 10935, 10936, 10937, 10938, 10939, 10940, 10941, 10942, 10943, 10944, 10945, 10946, 10947, 10948, 10949, 10950, 10951, 10952, 10953, 10954, 10955, 10956, 10957, 10958, 10959, 10960, 10961, 10962, 10963, 10964, 10965, 10966, 10967, 10968, 10969, 10970, 10971, 10972, 10973, 10974, 10975, 10976, 10977, 10978, 10979, 10980, 10981, 10982, 10983, 10984, 10985, 10986, 10987, 10988, 10989, 10990, 10991, 10992, 10993, 10994, 10995, 10996, 10997, 10998, 10999, 11000, 11001, 11002, 11003, 11004, 11005, 11006, 11007, 11008, 11009, 11010, 11011, 11012, 11013, 11014, 11015, 11016, 11017, 11018, 11019, 11020, 11021, 11022, 11023, 11024, 11025, 11026, 11027, 11028, 11029, 11030, 11031, 11032, 11033, 11034, 11035, 11036, 11037, 11038, 11039, 11040, 11041, 11042, 11043, 11044, 11045, 11046, 11047, 11048, 11049, 11050, 11051, 11052, 11053, 11054, 11055, 11056, 11057, 11058, 11059, 11060, 11061, 11062, 11063, 11064, 11065, 11066, 11067, 11068, 11069, 11070, 11071, 11072, 11073, 11074, 11075, 11076, 11077, 11078, 11079]).values())

    # current_object_type = list(Uploaded_dataset.objects.filter(id=79).values())
    # for i in range(len(current_object_type)):
    #     del current_object_type[i]['created']
    #     del current_object_type[i]['updated']
    #     del current_object_type[i]['data_generation_date']

    return HttpResponse(json.dumps(current_object_type))
    # return render(request, 'tool/test_page3.html')



    



