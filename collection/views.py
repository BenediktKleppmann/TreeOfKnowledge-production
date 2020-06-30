####################################################################
# This file is part of the Tree of Knowledge project.
# Copyright (c) 2019-2040 Benedikt Kleppmann

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version - see http://www.gnu.org/licenses/.
#####################################################################


from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset, Object_hierachy_tree_history, Attribute, Object_types, Data_point, Object, Calculation_rule, Learned_rule, Rule, Execution_order, Likelihood_fuction, Rule_parameter
from django.contrib.auth.models import User
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
import pdb
from boto import sns



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


# @login_required
# def get_available_variables(request):
#     object_type_id = request.GET.get('object_type_id', '')
#     available_variables = []
#     list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
#     for parent_object in list_of_parent_objects:
#         available_variables.extend(list(Attribute.objects.filter(first_applicable_object_type=parent_object['id']).values('name', 'id', 'data_type')))
#     return HttpResponse(json.dumps(available_variables))
    


# used in edit_model.html
@login_required
def get_object_rules(request):
    print('----------- get_object_rules -------------')
    object_type_id = request.GET.get('object_type_id', '')

    response = {}
    list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
    parent_object_type_ids = [obj['id'] for obj in list_of_parent_objects]
    print('parent_object_type_ids: ' + str(parent_object_type_ids))
    attributes = Attribute.objects.filter(first_applicable_object_type__in=parent_object_type_ids).values()
    
    print('attributes: ' + str(attributes))
    for attribute in attributes:
        response[attribute['id']] = {}
        rules_list = list(Rule.objects.filter(changed_var_attribute_id=attribute['id']).values())
        for rule in rules_list:
            rule['used_attribute_ids'] = json.loads(rule['used_attribute_ids'])
            rule['used_parameter_ids'] = json.loads(rule['used_parameter_ids'])

            # calculate 'probability' and 'standard_dev'
            histogram, mean, standard_dev, nb_of_values_in_posterior, nb_of_simulations = get_from_db.get_rules_pdf(rule['id'], True)
            rule['probability'] = None if mean is None or np.isnan(mean) else mean 
            rule['standard_dev'] = None if standard_dev is None or np.isnan(standard_dev) else standard_dev 


            # specify a default for 'learn_posterior'
            rule['learn_posterior'] = False
            if not rule['has_probability_1'] and rule['probability'] is None:
                rule['learn_posterior'] = True

            response[attribute['id']][rule['id']] = rule
    return HttpResponse(json.dumps(response)) 


# used in edit_object_behaviour_modal.html (which in turn is used in edit_simulation.html and analyse_simulation.html)
@login_required
def get_rules_pdf(request):
    print('====================   get_rules_pdf   ==================================')
    rule_or_parameter_id = request.GET.get('rule_or_parameter_id', '')
    is_rule = (request.GET.get('is_rule', '').lower() == 'true')

    histogram, mean, standard_dev, nb_of_values_in_posterior, nb_of_simulations = get_from_db.get_rules_pdf(rule_or_parameter_id, is_rule)
    response = {'nb_of_values_in_posterior': nb_of_values_in_posterior,
                'nb_of_simulations': nb_of_simulations}

    if histogram is None:
        return HttpResponse('null')
    
    # only smoothen out the function if the y-values vary significantly
    smooth_pdf = False
    # smooth_pdf = (np.std(histogram[0]) >= 0.15)
    if smooth_pdf:
        hist_dist = scipy.stats.rv_histogram(histogram)
        hist_sample = hist_dist.rvs(size=50000)
        a, b, min_value, value_range = beta.fit(hist_sample) 
        x_values = list(histogram[1])[:-1]
        pdf_values = [beta.pdf(x,a,b) for x in x_values]
        # the beta distributions sometimes goes to infinity for x=0 or x-1, the following things are to stop that...
        if pdf_values[0] > 100:
            pdf_values[0] = pdf_values[1]
        if pdf_values[29] > 100:
            pdf_values[29] = pdf_values[28]
        pdf_values = np.minimum(pdf_values, 100)
        response['pdf'] = [[x, min(prob,100)] for x, prob in zip(x_values, pdf_values)]
    else:
        response['pdf'] = [[bucket_value, min(count,10000)] for bucket_value, count in zip(histogram[1], histogram[0])]
    return HttpResponse(json.dumps(response))


# used in edit_object_behaviour_modal.html (which in turn is used in edit_simulation.html and analyse_simulation.html)
@login_required
def get_single_pdf(request):
    response = {}
    simulation_id = request.GET.get('simulation_id', '')
    object_number = request.GET.get('object_number', '')
    rule_or_parameter_id = request.GET.get('rule_or_parameter_id', '')
    is_rule = (request.GET.get('is_rule', '').lower() == 'true')
    histogram, mean, standard_dev, nb_of_values_in_posterior, message = get_from_db.get_single_pdf(simulation_id, object_number, rule_or_parameter_id, is_rule)
    print('====================   get_single_pdf   ==================================')
    print(str(rule_or_parameter_id))
    print(str(simulation_id))
    print(str(object_number))
    print(str(rule_or_parameter_id))
    print(str(is_rule))
    print(str(histogram is None))
    print(str(histogram))
    print('=========================================================================')
    response['nb_of_values_in_posterior'] = nb_of_values_in_posterior
    if message != '':
        response['message'] = message

    if histogram is None:
        return HttpResponse('null')

    # only smoothen out the function if the y-values vary significantly
    smooth_pdf = False
    # smooth_pdf = (np.std(histogram[0]) >= 0.15)
    if smooth_pdf:
        print(histogram)
        hist_dist = scipy.stats.rv_histogram(histogram)
        hist_sample = hist_dist.rvs(size=50000)
        a, b, min_value, value_range = beta.fit(hist_sample) 
        x_values = list(histogram[1])[:-1]
        pdf_values = [beta.pdf(x,a,b) for x in x_values]
        # the beta distributions sometimes goes to infinity for x=0 or x-1, the following things are to stop that...
        if pdf_values[0] > 100:
            pdf_values[0] = pdf_values[1]
        if pdf_values[29] > 100:
            pdf_values[29] = pdf_values[28]
        pdf_values = np.minimum(pdf_values, 100)
        response['pdf'] = [[x, prob] for x, prob in zip(x_values, pdf_values)]
    else:
        response['pdf'] = [[bucket_value, count] for bucket_value, count in zip(histogram[1], histogram[0])]
    return HttpResponse(json.dumps(response))
    


# used in edit_object_type_behaviour.html
@login_required
def get_parameter_info(request):
    parameter_id = request.GET.get('parameter_id', '')
    is_last_parameter = (request.GET.get('is_last_parameter', '').lower() == 'true')
    parameter_id = int(parameter_id)
    parameter_record = Rule_parameter.objects.get(id=parameter_id)
    parameter_info = {  'id': parameter_id,
                        'rule_id':parameter_record.rule_id, 
                        'parameter_name':parameter_record.parameter_name,
                        'min_value':parameter_record.min_value,
                        'max_value':parameter_record.max_value,
                        'is_last_parameter':is_last_parameter}


    return HttpResponse(json.dumps(parameter_info))   



@login_required
def get_execution_order(request):
    
    print('------------------ get_execution_order --------------------------------')
    execution_order_id = int(request.GET.get('execution_order_id', '1'))
    print('test')
    execution_order = json.loads(Execution_order.objects.get(id=execution_order_id).execution_order)
    # CORRECT TO CURRENT objects, attributes and rules

    # PART 1A: extend with missing objects, attributes 
    all_object_type_ids = [el[0] for el in list(Object_types.objects.all().values_list('id'))]
    for object_type_id in all_object_type_ids:
        list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
        list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]
        all_attributes = list(Attribute.objects.all().filter(first_applicable_object_type__in=list_of_parent_object_ids).values('id', 'name'))

        
        if object_type_id not in execution_order['attribute_execution_order'].keys():
            execution_order['attribute_execution_order'][object_type_id] = {'used_attributes':all_attributes, 'not_used_attributes': []}
        else:
            listed_attributes = execution_order['attribute_execution_order'][object_type_id]['used_attributes'] + execution_order['attribute_execution_order'][object_type_id]['not_used_attributes']
            listed_attribute_ids = set([attribute['id'] for attribute in listed_attributes])
            all_attribute_ids = set([attribute['id'] for attribute in all_attributes])
            if len(listed_attribute_ids) < len(all_attribute_ids):
                missing_attribute_ids = list(all_attribute_ids - listed_attribute_ids)
                missing_attributes = [attribute for attribute in all_attributes if attribute['id'] in missing_attribute_ids]
                execution_order['attribute_execution_order'][object_type_id]['used_attributes'] += missing_attribute_ids

    # PART 1B: extend with missing attributes, rules
    all_attribute_ids = [el[0] for el in list(Attribute.objects.all().values_list('id'))]
    for attribute_id in all_attribute_ids:
        all_rule_ids = [el[0] for el in list(Rule.objects.all().filter(changed_var_attribute_id=attribute_id).values_list('id'))]

        if (str(attribute_id) not in execution_order['rule_execution_order'].keys()):
            execution_order['rule_execution_order'][str(attribute_id)] = {'used_rule_ids': all_rule_ids, 'not_used_rule_ids': []}
        else:
            listed_rule_ids = set(execution_order['rule_execution_order'][str(attribute_id)]['used_rule_ids'] + execution_order['rule_execution_order'][str(attribute_id)]['not_used_rule_ids'])
            if len(listed_rule_ids) < len(all_rule_ids):
                missing_rule_ids = list(set(all_rule_ids) - listed_rule_ids)
                execution_order['rule_execution_order'][str(attribute_id)]['used_rule_ids'] += missing_rule_ids


    # PART 2A: remove no-longer-existing objects
    no_longer_existing_object_type_ids = set(execution_order['attribute_execution_order'].keys()) - set(all_object_type_ids)
    for no_longer_existing_object_type_id in no_longer_existing_object_type_ids:
        del execution_order['attribute_execution_order'][no_longer_existing_object_type_id]

    # PART 2B: remove no-longer-existing attributes 
    for object_type_id in all_object_type_ids:
        # used_attributes
        used_attributes = execution_order['attribute_execution_order'][object_type_id]['used_attributes']
        used_attribute_ids = [attribute['id'] for attribute in used_attributes]
        no_longer_existing_attribute_ids = set(used_attribute_ids) - set(all_attribute_ids)
        if len(no_longer_existing_attribute_ids)>0:
            new_used_attributes = [attribute for attribute in used_attributes if attribute['id'] not in no_longer_existing_attribute_ids]
            execution_order['attribute_execution_order'][object_type_id]['used_attributes'] = new_used_attributes

        # not_used_attributes
        not_used_attributes = execution_order['attribute_execution_order'][object_type_id]['not_used_attributes']
        not_used_attribute_ids = [attribute['id'] for attribute in not_used_attributes]
        no_longer_existing_attribute_ids = set(not_used_attribute_ids) - set(all_attribute_ids)
        if len(no_longer_existing_attribute_ids)>0:
            new_not_used_attributes = [attribute for attribute in not_used_attributes if attribute['id'] not in no_longer_existing_attribute_ids]
            execution_order['attribute_execution_order'][object_type_id]['not_used_attributes'] = new_not_used_attributes

    # PART 2C: remove no-longer-existing attributes 
    all_attribute_ids = [str(el) for el in all_attribute_ids]
    no_longer_existing_attribute_ids = set(execution_order['rule_execution_order'].keys()) - set(all_attribute_ids)
    for no_longer_existing_attribute_id in no_longer_existing_attribute_ids:
        del execution_order['rule_execution_order'][no_longer_existing_attribute_id]


    # PART 2D: remove no-longer-existing rules 
    all_rule_ids = [el[0] for el in list(Rule.objects.all().values_list('id'))]
    for attribute_id in execution_order['rule_execution_order'].keys():
        # used_rule_ids
        used_rule_ids = execution_order['rule_execution_order'][attribute_id]['used_rule_ids']
        no_longer_existing_rule_ids = set(used_rule_ids) - set(all_rule_ids)
        if len(no_longer_existing_rule_ids)>0:
            new_used_rule_ids = [rule_id for rule_id in used_rule_ids if rule_id not in no_longer_existing_rule_ids]
            execution_order['rule_execution_order'][attribute_id]['used_rule_ids'] = new_used_rule_ids

        # not_used_rule_ids
        not_used_rule_ids = execution_order['rule_execution_order'][attribute_id]['not_used_rule_ids']
        no_longer_existing_rule_ids = set(not_used_rule_ids) - set(all_rule_ids)
        if len(no_longer_existing_rule_ids)>0:
            new_not_used_rule_ids = [rule_id for rule_id in not_used_rule_ids if rule_id not in no_longer_existing_rule_ids]
            execution_order['rule_execution_order'][attribute_id]['not_used_rule_ids'] = new_not_used_rule_ids
    return HttpResponse(json.dumps(execution_order))


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
    simulation_id = request_body['simulation_id']
    objects_dict = request_body['objects_dict']
    environment_start_time = request_body['environment_start_time']
    environment_end_time = request_body['environment_end_time']


    objects_data = query_datapoints.get_data_from_random_related_object(simulation_id, objects_dict, environment_start_time, environment_end_time)
    data_querying_info = Simulation_model.objects.get(id=simulation_id).data_querying_info
    response = {'objects_data': objects_data, 
                'data_querying_info': data_querying_info}               
    return HttpResponse(json.dumps(response))


# used in query_data.html
@login_required
def get_data_from_objects_behind_the_relation(request):
    request_body = json.loads(request.body)
    object_type_id = request_body['object_type_id']
    object_ids = request_body['object_ids']
    object_ids = list(set([el for el in object_ids if el])) #distinct not-null values
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
    relation_id = int(request.GET.get('relation_id', ''))
    print('++++++++ ' + str(relation_id) + ' +++++++++++++++++')
    attribute_id = request.GET.get('attribute_id', '')
    value = request.GET.get('value', '')

    matching_object_id = query_datapoints.find_single_entity(relation_id, attribute_id, value)
    print(str(matching_object_id))
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
            attribute_record.format_specification = json.dumps(request_body['format_specification'])
            attribute_record.first_applicable_object_type = request_body['first_applicable_object_type']
            attribute_record.first_relation_object_type=request_body['first_relation_object_type']
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
            

            if ('id' in request_body.keys()):
                rule_id = request_body['id']
                rule_record = Rule.objects.get(id=rule_id)
                rule_record.changed_var_attribute_id = request_body['changed_var_attribute_id']
                rule_record.changed_var_data_type = request_body['changed_var_data_type']
                rule_record.condition_text = request_body['condition_text']
                rule_record.condition_exec = request_body['condition_exec']
                rule_record.effect_text = request_body['effect_text']
                rule_record.effect_exec = request_body['effect_exec']
                rule_record.effect_is_calculation = request_body['effect_is_calculation']
                rule_record.used_attribute_ids = json.dumps(request_body['used_attribute_ids'])
                rule_record.used_parameter_ids = json.dumps(request_body['used_parameter_ids'])
                rule_record.is_conditionless = request_body['is_conditionless']
                rule_record.has_probability_1 = request_body['has_probability_1']
                rule_record.save()

                # reset all likelihood functions associated with this rule
                likelihood_fuctions = Likelihood_fuction.objects.filter(rule_id=rule_id)
                for likelihood_fuction in likelihood_fuctions:
                    likelihood_fuction.list_of_probabilities = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                    likelihood_fuction.save()

                rule_parameters = Rule_parameter.objects.filter(rule_id=rule_id)
                for rule_parameter in rule_parameters:
                    likelihood_fuctions = Likelihood_fuction.objects.filter(parameter_id=rule_parameter.id)
                    for likelihood_fuction in likelihood_fuctions:
                        likelihood_fuction.list_of_probabilities = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                        likelihood_fuction.save()


            else:
                new_entry = Rule(changed_var_attribute_id= request_body['changed_var_attribute_id'],
                                changed_var_data_type= request_body['changed_var_data_type'],
                                condition_text= request_body['condition_text'],
                                condition_exec= request_body['condition_exec'],
                                effect_text= request_body['effect_text'],
                                effect_exec= request_body['effect_exec'],
                                effect_is_calculation= request_body['effect_is_calculation'],
                                used_attribute_ids= json.dumps(request_body['used_attribute_ids']),
                                used_parameter_ids= json.dumps(request_body['used_parameter_ids']),
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
            model_record.sorted_attribute_ids = json.dumps(request_body['sorted_attribute_ids'])
            model_record.object_type_counts = json.dumps(request_body['object_type_counts'])
            model_record.total_object_count = request_body['total_object_count']
            model_record.number_of_additional_object_facts = request_body['number_of_additional_object_facts']
            model_record.execution_order_id = request_body['execution_order_id']
            model_record.environment_start_time = request_body['environment_start_time']
            model_record.environment_end_time = request_body['environment_end_time']
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




# used in: edit_simulation__simulate (the edit_object_type_modal)
@login_required
def save_rule_parmeter(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            simulation_id = request_body['simulation_id']
            object_number = request_body['object_number']
            rule_id = request_body['rule_id']
            new_parameter_dict = request_body['new_parameter_dict']
            if ('id' in request_body):
                parameter = Rule_parameter.objects.get(id=request_body['id'])
                parameter.rule_id = new_parameter_dict['rule_id']
                parameter.parameter_name = new_parameter_dict['parameter_name']
                parameter.min_value = new_parameter_dict['min_value']
                parameter.max_value = new_parameter_dict['max_value']
                parameter.save()

                # if the range was changed: reset the parameter's likelihood_fuctions
                if request_body['parameter_range_change']:
                    Likelihood_fuction.objects.filter(parameter_id=request_body['id']).delete()
                    list_of_probabilities = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                    likelihood_fuction = Likelihood_fuction(simulation_id=simulation_id, object_number=object_number, parameter_id=request_body['id'], list_of_probabilities=list_of_probabilities, nb_of_simulations=0, nb_of_sim_in_which_rule_was_used=0, nb_of_values_in_posterior=0)
                    likelihood_fuction.save()


                return_dict = {'parameter_id': parameter.id, 'is_new': False, 'request_body':request_body}
                return HttpResponse(json.dumps(return_dict))
            else:
                new_parameter = Rule_parameter(rule_id=new_parameter_dict['rule_id'], parameter_name=new_parameter_dict['parameter_name'], min_value=new_parameter_dict['min_value'], max_value=new_parameter_dict['max_value'])
                new_parameter.save()

                # add to used_parameter_ids of parent rule
                parent_rule = Rule.objects.get(id=new_parameter_dict['rule_id'])
                used_parameter_ids = json.loads(parent_rule.used_parameter_ids)
                parent_rule.used_parameter_ids = used_parameter_ids + [new_parameter.id]
                parent_rule.save()
  
                # add uniform likelihood_function
                list_of_probabilities = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                likelihood_fuction = Likelihood_fuction(simulation_id=simulation_id, object_number=object_number, parameter_id=new_parameter.id, list_of_probabilities=list_of_probabilities, nb_of_simulations=0, nb_of_sim_in_which_rule_was_used=0, nb_of_values_in_posterior=0)
                likelihood_fuction.save()

                return_dict = {'parameter_id': new_parameter.id, 'is_new': True, 'request_body':request_body}
                return HttpResponse(json.dumps(return_dict))

        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")



# used in: edit_simulation__simulate (the edit_object_type_modal)
@login_required
def save_likelihood_function(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            if ('id' in request_body):
                likelihood_function = Likelihood_fuction.objects.get(id=request_body['id'])
                likelihood_function.simulation_id = request_body['simulation_id']
                likelihood_function.object_number = request_body['object_number']
                likelihood_function.parameter_id = request_body['parameter_id']
                likelihood_function.list_of_probabilities = json.dumps(request_body['list_of_probabilities'])
                likelihood_function.nb_of_simulations = request_body['nb_of_simulations']
                likelihood_function.nb_of_sim_in_which_rule_was_used = request_body['nb_of_sim_in_which_rule_was_used']
                likelihood_function.nb_of_values_in_posterior = request_body['nb_of_values_in_posterior']
                likelihood_function.save()
                return HttpResponse(str(likelihood_function.id))
            else:
                new_likelihood_function = Likelihood_fuction(simulation_id=request_body['simulation_id'], object_number=request_body['object_number'], parameter_id=request_body['parameter_id'], list_of_probabilities=json.dumps(request_body['list_of_probabilities']), nb_of_simulations=request_body['nb_of_simulations'], nb_of_sim_in_which_rule_was_used=request_body['nb_of_sim_in_which_rule_was_used'], nb_of_values_in_posterior=request_body['nb_of_values_in_posterior'])
                new_likelihood_function.save()
                return HttpResponse(str(new_likelihood_function.id))
        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")




# used in: edit_simulation__simulate (the saveSimulation function)
@login_required
def save_execution_order(request):
    print('-------  save_execution_order  -----------')
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            if ('id' in request_body):
                execution_order_record = Execution_order.objects.get(id=request_body['id'])
                execution_order_record.name = request_body['name']
                execution_order_record.description = request_body['description']
                execution_order_record.execution_order = json.dumps(request_body['execution_order'])
                execution_order_record.save()
                return HttpResponse(str(execution_order_record.id))
            else:
                execution_order_record = Execution_order(name=name,description=request_body['description'], execution_order=json.dumps(request_body['execution_order']))
                execution_order_record.save()
                return HttpResponse(str(execution_order_record.id))
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
            rule = Rule.objects.get(id=rule_id)
            rule.delete()

            likelihood_fuctions = Likelihood_fuction.objects.filter(rule_id=rule_id)
            likelihood_fuctions.delete()

            rule_parameters = Rule_parameter.objects.filter(rule_id=rule_id)
            rule_parameters.delete()
            return HttpResponse("success")

        except Exception as error:
            traceback.print_exc()
            return HttpResponse(str(error))
    else:
        return HttpResponse("This must be a POST request.")



# used in: edit_simulation__simulate.html
@login_required
def delete_parameter(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
            parameter_id = request_body['parameter_id']
            parameter = Rule_parameter.objects.get(id=parameter_id)
            parameter.delete()

            likelihood_fuctions = Likelihood_fuction.objects.filter(parameter_id=parameter_id)
            likelihood_fuctions.delete()
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
    print('-----------------------------------------------------------')
    print(value)

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

    if operator == '=':
        violating_columns = tdda_functions.get_columns_format_violations(attribute_id, [value])
        if len(violating_columns) > 0:
            format_violation_text = 'The value "' + str(value) + '" does not satisfy the required format for ' + attribute_name + '-values. <br />'
            format_violation_text += 'It must satisfy: <ul>'
            for key in format_specification['fields']['column'].keys():
                format_violation_text += '<li>' + str(key) + ' = ' + str(format_specification['fields']['column'][key]) + '</li>'
            format_violation_text += '</ul>'
            response['format_violation_text'] = format_violation_text
            return HttpResponse(json.dumps(response))

    if operator == 'in':
        list_of_values = json.loads(value)
        for individual_value in list_of_values:
            violating_columns = tdda_functions.get_columns_format_violations(attribute_id, [individual_value])
            if len(violating_columns) > 0:
                format_violation_text = 'The value "' + str(individual_value) + '" does not satisfy the required format for ' + attribute_name + '-values. <br />'
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
                                        sorted_attribute_ids=json.dumps([]), 
                                        object_type_counts=json.dumps({}),
                                        total_object_count=0,
                                        number_of_additional_object_facts=2,
                                        execution_order_id=1,
                                        not_used_rules='{}',
                                        environment_start_time=946684800, 
                                        environment_end_time=1577836800, 
                                        simulation_start_time=946684800, 
                                        simulation_end_time=1577836800, 
                                        timestep_size=31622400,
										validation_data='{}',
										data_querying_info='{"timestamps":{}, "table_sizes":{}, "relation_sizes":{}}')
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


    
    available_object_types = get_from_db.get_most_commonly_used_object_types()
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
#     for index in range(len(times)):
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
def admin_page(request):
    number_of_users = User.objects.count()
    number_of_newsletter_subscribers = Newsletter_subscriber.objects.count()
    return render(request, 'admin/admin_page.html', {'number_of_users': number_of_users, 'number_of_newsletter_subscribers': number_of_newsletter_subscribers})


# ==================
# INSPECT
# ==================

@staff_member_required
def inspect_object(request, object_id):
    return render(request, 'admin/inspect_object.html', {'object_id': object_id})

@staff_member_required
def get_object(request):
    object_id = request.GET.get('object_id', '')
    individual_object = admin_fuctions.inspect_individual_object(object_id)
    return HttpResponse(json.dumps(individual_object))

@staff_member_required
def inspect_upload(request, upload_id):
    return render(request, 'admin/inspect_upload.html', {'upload_id': upload_id})

@staff_member_required
def get_uploaded_dataset(request):
    upload_id = request.GET.get('upload_id', None)
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id)
    uploaded_dataset_dict = {   'data_table_json':json.loads(uploaded_dataset.data_table_json),
                                'object_id_column':json.loads(uploaded_dataset.object_id_column),
                                'data_source':uploaded_dataset.data_source,
                                'data_generation_date':uploaded_dataset.data_generation_date.strftime('%Y-%m-%d %H:%M'),
                                'correctness_of_data':uploaded_dataset.correctness_of_data,
                                'object_type_name':uploaded_dataset.object_type_name,
                                'meta_data_facts':uploaded_dataset.meta_data_facts}

    return HttpResponse(json.dumps(uploaded_dataset_dict))

# ==================
# SHOW
# ==================

@staff_member_required
def show_attributes(request):
    attributes = Attribute.objects.all()
    return render(request, 'admin/show_attributes.html', {'attributes': attributes,})

@staff_member_required
def show_object_types(request):
    object_types = Object_types.objects.all()
    return render(request, 'admin/show_object_types.html', {'object_types': object_types,})



@staff_member_required
def show_newsletter_subscribers(request):
    newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
    return render(request, 'admin/show_newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})

@staff_member_required
def show_users(request):
    users = User.objects.all()
    return render(request, 'admin/show_users.html', {'users': users,})



# ==================
# DATA CLEANING
# ==================

@staff_member_required
def possibly_duplicate_objects_without_keys(request):
    object_types = list(Object_types.objects.all().values())
    object_types_names = {str(object_type['id']):object_type['name'] for object_type in object_types}
    return render(request, 'admin/possibly_duplicate_objects_without_keys.html', {'object_types_names':object_types_names})


@staff_member_required
def find_possibly_duplicate_objects_without_keys(request):
    print('find_possibly_duplicate_objects_without_keys')
    admin_fuctions.find_possibly_duplicate_objects_without_keys()


@staff_member_required
def get_possibly_duplicate_objects_without_keys(request):
    with open('collection/static/webservice files/runtime_data/duplicate_objects_by_object_type.txt', 'r') as file:
        duplicate_objects_by_object_type = file.read().replace('\n', '')
    return HttpResponse(duplicate_objects_by_object_type)

# ----

@staff_member_required
def possibly_duplicate_objects_with_keys(request):
    object_types = list(Object_types.objects.all().values())
    object_types_names = {str(object_type['id']):object_type['name'] for object_type in object_types}
    return render(request, 'admin/possibly_duplicate_objects_with_keys.html', {'object_types_names':object_types_names})



@staff_member_required
def get_possibly_duplicate_objects_with_keys(request):
    object_type_id = request.GET.get('object_type_id', '')
    key_attribute_id = request.GET.get('key_attribute_id', '')
    possibly_duplicate_objects = admin_fuctions.get_possibly_duplicate_objects_with_keys(object_type_id, key_attribute_id)
    return HttpResponse(json.dumps(possibly_duplicate_objects))


# ----
@staff_member_required
def delete_objects_page(request):
    return render(request, 'admin/delete_objects.html')


@staff_member_required
def delete_objects(request):
    if request.method == 'POST':
        print('===================')
        print(request.body)
        object_ids = json.loads(request.body)
        print('+++++++++++++++++++++++')
        print(str(object_ids))
        Object.objects.filter(id__in=object_ids).delete()
        Data_point.objects.filter(object_id__in=object_ids).delete()
    return HttpResponse('Objects deleted!')


# ==================
# VARIOUS SCRIPTS
# ==================

@staff_member_required
def various_scripts(request):
    return render(request, 'admin/various_scripts.html',)


@staff_member_required
def remove_null_datapoints(request):
    print('views.remove_null_datapoints')
    admin_fuctions.remove_null_datapoints()
    return HttpResponse('success')

@staff_member_required
def remove_duplicate_datapoints(request):
    admin_fuctions.remove_duplicates()
    return HttpResponse('success')


@staff_member_required
def backup_database(request):
    success_for_object_types = admin_fuctions.backup_object_types()
    success_for_attributes = admin_fuctions.backup_attributes()

    if (success_for_object_types and success_for_attributes):
        return HttpResponse('success')
    else:
        return HttpResponse('An error occured')


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

    return render(request, 'admin/upload_file.html', {'errors': errors})



# ==================
# TEST PAGES
# ==================
def test_page1(request):
    import psycopg2
    connection = psycopg2.connect(user="dbadmin", password="rUWFidoMnk0SulVl4u9C", host="aa1pbfgh471h051.cee9izytbdnd.eu-central-1.rds.amazonaws.com", port="5432", database="postgres")
    cursor = connection.cursor()
    cursor.execute('''SELECT * 
                      FROM information_schema.tables
                      OFFSET 150;
                    ''')

    mobile_records = cursor.fetchall() 
   
    print("Print each row and it's columns values")
    for row in mobile_records:
        print("Id = ", row[0], )
        print("Model = ", row[1])
        print("Price  = ", row[2], "\n")


        # postgresql
        # SELECT id 
        # INTO unfiltered_object_ids_x
        # FROM unfiltered_object_ids_x;



        return HttpResponse(str(mobile_records))




def test_page2(request):
    import boto3
    sqs = boto3.client('sqs', region_name='eu-central-1')

    # queue = sqs.get_queue_by_name(QueueName='awseb-e-8ps6q6m3je-stack-AWSEBWorkerQueue-1RIUDLVL1OCH2')
    # queue_url = sqs.get_queue_url(QueueName='Treeofknowledge-queue')
    # response = queue.send_message(MessageBody='world')

    queue_url = 'https://sqs.eu-central-1.amazonaws.com/662304246363/Treeofknowledge-queue'
    response = sqs.send_message(QueueUrl= queue_url, MessageBody='{"sample json": "test"}')

    queue_url = 'https://sqs.eu-central-1.amazonaws.com/662304246363/awseb-e-qwnyj2drkn-stack-NewSignupQueue-1VKLS1VF5RHQF'
    response = sqs.send_message(QueueUrl= queue_url, MessageBody='Test3')



    # sns_conn = sns.connect_to_region('eu-central-1')
    # sns_conn.publish('arn:aws:sqs:eu-central-1:662304246363:awseb-e-8ps6q6m3je-stack-AWSEBWorkerQueue-1RIUDLVL1OCH2', '{"some test json":[3,4,5], "etc.":[1,2,3]}', "Test test test")

    return HttpResponse('success' + str(response))

    


def test_page3(request):
    # current_object_type = list(Data_point.objects.all().values('object_type_id').annotate(total=Count('object_type_id')))

    # current_object_type = list(Data_point.objects.filter(object_id=862638).values())
    # starttime = 1167436800
    # endtime = 1198972800
    # objects_dict = json.loads('{"1": {"object_name": "Household 1", "object_type_id": "j2_8", "object_type_name": "Household", "object_icon": "si-glyph-house", "object_id": 869390, "object_attributes": {"22": {"attribute_value": null, "attribute_name": "Name", "attribute_data_type": "string", "attribute_rule": null}, "148": {"attribute_value": 862351, "attribute_name": "Location (City)", "attribute_data_type": "relation", "attribute_rule": null}, "149": {"attribute_value": 862704, "attribute_name": "Location (City District/Quarter)", "attribute_data_type": "relation", "attribute_rule": null}, "150": {"attribute_value": 864250, "attribute_name": "Company owned by household member", "attribute_data_type": "relation", "attribute_rule": null}, "151": {"attribute_value": 5, "attribute_name": "Size/ Number of people", "attribute_data_type": "int", "attribute_rule": null}, "152": {"attribute_value": true, "attribute_name": "Male Head/Boss of the Group", "attribute_data_type": "bool", "attribute_rule": null}, "153": {"attribute_value": 4, "attribute_name": "Number of Adults", "attribute_data_type": "int", "attribute_rule": null}, "154": {"attribute_value": 1, "attribute_name": "Number of Children", "attribute_data_type": "int", "attribute_rule": null}, "155": {"attribute_value": 4682, "attribute_name": "Household ID used by the Centre for Microfinance (IFMR)", "attribute_data_type": "int", "attribute_rule": null}, "156": {"attribute_value": null, "attribute_name": "Monthly expenditure on education (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "157": {"attribute_value": null, "attribute_name": "Number of Women aged 18 to 45", "attribute_data_type": "int", "attribute_rule": null}, "158": {"attribute_value": true, "attribute_name": "Has children members", "attribute_data_type": "bool", "attribute_rule": null}, "159": {"attribute_value": false, "attribute_name": "Owns land in the city", "attribute_data_type": "bool", "attribute_rule": null}, "160": {"attribute_value": false, "attribute_name": "Owns land on the countryside", "attribute_data_type": "bool", "attribute_rule": null}, "161": {"attribute_value": 1800, "attribute_name": "Total wages (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "162": {"attribute_value": 168, "attribute_name": "Total hours worked a week", "attribute_data_type": "real", "attribute_rule": null}, "163": {"attribute_value": 168, "attribute_name": "Total hours per week working for own business", "attribute_data_type": "real", "attribute_rule": null}, "164": {"attribute_value": 0, "attribute_name": "Total hours per week working outside", "attribute_data_type": "real", "attribute_rule": null}, "166": {"attribute_value": 0, "attribute_name": "Total hours worked per week by children aged 16-20", "attribute_data_type": "real", "attribute_rule": null}, "167": {"attribute_value": 7666.3335, "attribute_name": "Monthly expenditure (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "168": {"attribute_value": 6999.6665, "attribute_name": "Monthly expenditure on non-durable goods (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "169": {"attribute_value": 666.6667, "attribute_name": "Monthly expenditure on durable goods (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "170": {"attribute_value": 466.66666, "attribute_name": "Monthly expenditure on health (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "171": {"attribute_value": 746.6667, "attribute_name": "Monthly expenditure on education (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "172": {"attribute_value": 9500, "attribute_name": "Monthly expenditure on celebrations (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "173": {"attribute_value": 300, "attribute_name": "Monthly expenditure on temptation goods (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "174": {"attribute_value": 3279, "attribute_name": "Monthly expenditure on food (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "175": {"attribute_value": true, "attribute_name": "Has Microfinance Loan", "attribute_data_type": "bool", "attribute_rule": null}, "176": {"attribute_value": false, "attribute_name": "Has Bank Loan", "attribute_data_type": "bool", "attribute_rule": null}, "177": {"attribute_value": true, "attribute_name": "Has Informal Loan", "attribute_data_type": "bool", "attribute_rule": null}, "178": {"attribute_value": true, "attribute_name": "Has Loan", "attribute_data_type": "bool", "attribute_rule": null}, "179": {"attribute_value": 8000, "attribute_name": "Amount loaned from Microfinance Institution (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "180": {"attribute_value": 0, "attribute_name": "Amount loaned from banks (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "181": {"attribute_value": 301800, "attribute_name": "Amount loaned from friends & relatives (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}, "182": {"attribute_value": 344800, "attribute_name": "Dept (ppp adjusted $)", "attribute_data_type": "real", "attribute_rule": null}}, "object_rules": {"22": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "148": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "149": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "150": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "151": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "152": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "153": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "154": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "155": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "156": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "157": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "158": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "159": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "160": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "161": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "162": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "163": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "164": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "166": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "167": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "168": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "169": {"used_rules": {"21": {"id": 21, "changed_var_attribute_id": 169, "changed_var_data_type": "real", "condition_text": "[Location (City District/Quarter)].[Has Microfinance Institution]", "condition_exec": "df.rel149.attr131", "effect_text": "[Monthly expenditure on durable goods (ppp adjusted $)]* 1.1/[delta_t (years)]", "effect_exec": "df.attr169* 1.1/(df.delta_t/31622400)", "effect_is_calculation": true, "used_attribute_ids": "[''149'', ''131'', ''169'']", "is_conditionless": false, "has_probability_1": false, "probability": null, "standard_dev": null, "learn_posterior": true}}, "not_used_rules": {}, "execution_order": [21]}, "170": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "171": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "172": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "173": {"used_rules": {"22": {"id": 22, "changed_var_attribute_id": 173, "changed_var_data_type": "real", "condition_text": "[Location (City District/Quarter)].[Has Microfinance Institution]", "condition_exec": "df.rel149.attr131", "effect_text": "[Monthly expenditure on temptation goods (ppp adjusted $)] * 0.9 / [delta_t (years)]", "effect_exec": "df.attr173 * 0.9 / (df.delta_t/31622400)", "effect_is_calculation": true, "used_attribute_ids": "[''149'', ''131'', ''173'']", "is_conditionless": false, "has_probability_1": false, "probability": null, "standard_dev": null, "learn_posterior": true}}, "not_used_rules": {}, "execution_order": [22]}, "174": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "175": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "176": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "177": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "178": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "179": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "180": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "181": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "182": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}}, "object_filter_facts": [], "object_relations": [{"relation_name": "Location (City District/Quarter)", "attribute_id": 149, "target_object_number": 2}], "position": {"x": 221, "y": 342}}, "2": {"object_name": "City District/Quarter/Borough 1", "object_type_id": "j2_4", "object_type_name": "City District/Quarter/Borough", "object_icon": "si-glyph-city", "object_id": 862704, "object_attributes": {"22": {"attribute_value": null, "attribute_name": "Name", "attribute_data_type": "string", "attribute_rule": null}, "23": {"attribute_value": null, "attribute_name": "Surface area (km2)", "attribute_data_type": "real", "attribute_rule": null}, "24": {"attribute_value": 537, "attribute_name": "Population", "attribute_data_type": "int", "attribute_rule": null}, "25": {"attribute_value": null, "attribute_name": "Infant mortality (%)", "attribute_data_type": "real", "attribute_rule": null}, "26": {"attribute_value": null, "attribute_name": "Life expectancy (years)", "attribute_data_type": "real", "attribute_rule": null}, "27": {"attribute_value": null, "attribute_name": "Maternal mortality ratio (%)", "attribute_data_type": "real", "attribute_rule": null}, "28": {"attribute_value": null, "attribute_name": "Population growth (%/year)", "attribute_data_type": "real", "attribute_rule": null}, "29": {"attribute_value": null, "attribute_name": "Life expectancy for women (years)", "attribute_data_type": "real", "attribute_rule": null}, "33": {"attribute_value": null, "attribute_name": "CO2 Emissions (tons/year)", "attribute_data_type": "real", "attribute_rule": null}, "35": {"attribute_value": null, "attribute_name": "Rural population with safe water (%)", "attribute_data_type": "real", "attribute_rule": null}, "36": {"attribute_value": null, "attribute_name": "People with safe water (%)", "attribute_data_type": "real", "attribute_rule": null}, "37": {"attribute_value": null, "attribute_name": "Urban population with safe water (%)", "attribute_data_type": "real", "attribute_rule": null}, "38": {"attribute_value": null, "attribute_name": "Rural population with safe sanitation (%)", "attribute_data_type": "real", "attribute_rule": null}, "39": {"attribute_value": null, "attribute_name": "People with safe sanitation (%)", "attribute_data_type": "real", "attribute_rule": null}, "40": {"attribute_value": null, "attribute_name": "Urban population with safe sanitation (%)", "attribute_data_type": "real", "attribute_rule": null}, "42": {"attribute_value": null, "attribute_name": "Male Population", "attribute_data_type": "int", "attribute_rule": null}, "57": {"attribute_value": null, "attribute_name": "Number of Companies in this area", "attribute_data_type": "int", "attribute_rule": null}, "58": {"attribute_value": null, "attribute_name": "Percentage of companies with an afro american owner", "attribute_data_type": "real", "attribute_rule": null}, "59": {"attribute_value": null, "attribute_name": "Percentage of companies with an american indian owner", "attribute_data_type": "real", "attribute_rule": null}, "60": {"attribute_value": null, "attribute_name": "Percentage of companies with an asian owner", "attribute_data_type": "real", "attribute_rule": null}, "61": {"attribute_value": null, "attribute_name": "Percentage of companies with an owner who is native hawaiian or other pacific islander", "attribute_data_type": "real", "attribute_rule": null}, "62": {"attribute_value": null, "attribute_name": "Percentage of companies with an hispanic owner", "attribute_data_type": "real", "attribute_rule": null}, "63": {"attribute_value": null, "attribute_name": "Percentage of companies owned by a woman", "attribute_data_type": "real", "attribute_rule": null}, "129": {"attribute_value": null, "attribute_name": "Location (city)", "attribute_data_type": "relation", "attribute_rule": null}, "130": {"attribute_value": 69, "attribute_name": "Area Id used by the Centre for Microfinance (IFMR)", "attribute_data_type": "int", "attribute_rule": null}, "131": {"attribute_value": true, "attribute_name": "Has Microfinance Institution", "attribute_data_type": "bool", "attribute_rule": null}}, "object_rules": {"22": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "23": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "24": {"used_rules": {"1": {"id": 1, "changed_var_attribute_id": 24, "changed_var_data_type": "int", "condition_text": "", "condition_exec": "", "effect_text": "[Population] + [Population]*([Population growth (%/year)] /100)* [delta_t (years)]", "effect_exec": "df.attr24 + df.attr24*(df.attr28 /100)* (df.delta_t/31622400)", "effect_is_calculation": true, "used_attribute_ids": "[''24'', ''28'']", "is_conditionless": true, "has_probability_1": true, "probability": null, "standard_dev": null, "learn_posterior": false}, "2": {"id": 2, "changed_var_attribute_id": 24, "changed_var_data_type": "int", "condition_text": "", "condition_exec": "", "effect_text": "[Population] + ([Female Population]*[Fertility rate]/[Life expectancy for women (years)] ) - ([Population]/[Life expectancy (years)])", "effect_exec": "df.attr24 + (df.attr41*df.attr31/df.attr29 ) - (df.attr24/df.attr26)", "effect_is_calculation": true, "used_attribute_ids": "[''24'', ''26'', ''29'', ''31'', ''41'']", "is_conditionless": true, "has_probability_1": true, "probability": 0.5152553763440862, "standard_dev": 0.28451725640376385, "learn_posterior": false}}, "not_used_rules": {}, "execution_order": [1, 2]}, "25": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "26": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "27": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "28": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "29": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "33": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "35": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "36": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "37": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "38": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "39": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "40": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "42": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "57": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "58": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "59": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "60": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "61": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "62": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "63": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "129": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "130": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}, "131": {"used_rules": {}, "not_used_rules": {}, "execution_order": []}}, "object_filter_facts": [], "object_relations": [], "position": {"x": 409, "y": 163}}}')
    # period_df = query_datapoints.get_data_from_related_objects(objects_dict, starttime, endtime)
    # print(period_df)
    # for i in range(len(current_object_type)):
    #     del current_object_type[i]['created']
    #     del current_object_type[i]['updated']
    #     del current_object_type[i]['data_generation_date']

    # return HttpResponse(json.dumps(current_object_type))
    # list_of_object_ids = list(Object.objects.all().values_list(['id','object_type_id']))
    # return HttpResponse('success')
    print('test_page3 - 1')
    execution_order__object_attributes = {}
    object_type_ids = [el[0] for el in list(Object_types.objects.all().values_list('id'))]
    for object_type_id in object_type_ids:
        list_of_parent_objects = get_from_db.get_list_of_parent_objects(object_type_id)
        list_of_parent_object_ids = [el['id'] for el in list_of_parent_objects]
        attribute_ids = [el[0] for el in list(Attribute.objects.all().filter(first_applicable_object_type__in=list_of_parent_object_ids).values_list('id'))]
        execution_order__object_attributes[object_type_id] = attribute_ids


    execution_order__attribute_rules = {}
    attribute_ids = [el[0] for el in list(Attribute.objects.all().values_list('id'))]
    for attribute_id in attribute_ids:
        rule_ids = [el[0] for el in list(Rule.objects.all().filter(changed_var_attribute_id=attribute_id).values_list('id'))]
        execution_order__attribute_rules[attribute_id] = rule_ids


    execution_order = {'object_attributes': execution_order__object_attributes, 'attribute_rules': execution_order__attribute_rules}
    return HttpResponse(json.dumps(execution_order))
    # return render(request, 'tool/test_page3.html')



    



