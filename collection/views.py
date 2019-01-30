from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset, Object_hierachy_tree_history#, Attribute
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3, Uploaded_datasetForm4, Uploaded_datasetForm5, Uploaded_datasetForm6
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
        request.POST = request.POST.copy()
        for fact_number in range(1,19):
            if 'attribute' + str(fact_number) in request.POST.keys():
                if request.POST['attribute' + str(fact_number)] == '':
                    request.POST.pop('attribute' + str(fact_number))
                    request.POST.pop('operator' + str(fact_number))
                    request.POST.pop('value' + str(fact_number))
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
            new_model_id = upload_data.perform_uploading(uploaded_dataset)
            return redirect('upload_data_success', new_model_id=new_model_id)
   
    return render(request, 'tree_of_knowledge_frontend/upload_data6.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})


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



@login_required
def upload_data5__edit_column(request): 
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



@login_required
def upload_data5__get_columns_format_violations(request):
    request_body = json.loads(request.body)
    attribute_name = request_body['attribute_name']
    column_values = request_body['column_values']

    # constraint_dict = get_from_db.get_attribute_constraints(attribute_name)
    # df = pd.DataFrame({'column':column_values})
    # pdv = PandasConstraintVerifier(df, epsilon=None, type_checking=None)

    # constraints = DatasetConstraints()
    # constraints.initialize_from_dict(constraint_dict)

    # pdv.repair_field_types(constraints)
    # detection = pdv.detect(constraints, VerificationClass=PandasDetection, outpath=None, write_all=False, per_constraint=False, output_fields=None, index=False, in_place=False, rownumber_is_index=True, boolean_ints=False, report='records') 
    # violation_df = detection.detected()
    # violating_columns = [int(col_nb) for col_nb in list(violation_df.index.values)]

    violating_columns = tdda_functions.get_columns_format_violations(attribute_name, column_values)
    return HttpResponse(json.dumps(violation_columns))



@login_required
def upload_data5__suggest_attribute_format(request): 
    column_dict = json.loads(request.body)
    # df = pd.DataFrame(column_dict)
    # constraints = discover_df(df, inc_rex=False)
    # constraints_dict = constraints.to_dict()
    constraints_dict = tdda_functions.suggest_attribute_format(column_dict)
    return HttpResponse(json.dumps(constraints_dict))

@login_required
def check_single_fact_format(request):
    format_violation_text = '';
#     attribute = request.GET.get('attribute', '')
#     operator = request.GET.get('operator', '')
#     value = request.GET.get('value', '')

#     if (attribute != '') and (value != ''):
#         attribute_constraints = get_from_db.get_attribute_constraints(attribute)
#         attribute_dtype = attribute_constraints['fields']['column']['type']

#         attribute_record = Attribute.objects.get(id=attribute)
#         if attribute_record is not None:
#             format_violation_text += 'The attribute "' + attribute + '"" does not yet exist.\n\n'

#         if (operator not in ['=', '>', '<', 'in']):
#             format_violation_text += '"' + operator +'" is not a valid operator.\n\n'

#         if (operator == 'in') and (attribute_constraints['fields']['column']['allowed_values'] is None):
#             format_violation_text += 'The "in" operator is only permitted for categorical attributes'

#         if (operator in ['>', '<']) and (attribute_constraints['fields']['column']['allowed_values'] is None):
#             format_violation_text += 'The "<" and ">" operators are only permitted for attributes with type "real" or "int"'

#         # TO DO: check if value is truly an int (for int) or float (for real)

#         # TO DO: if int or real, first convert value to int of float, respectively


#         violating_columns = get_columns_format_violations(attribute, [value])
#         if len(violating_columns) > 0:
#             format_violation_text += 'The value "' + + '" does not satisfy the format for ' + attribute + '-values. \n'
#             format_violation_text += 'It must satisfy: \n'
#             for key in attribute_constraints['fields']['column'].keys():
#                 format_violation_text += '•   ' + key + ' = ' + attribute_constraints['fields']['column'][key] + '\n'

    return format_violation_text
















@login_required
def get_possible_attributes(request):
    print("object_type = %s" % request.GET.get('object_type', ''))
    possible_attributes = ["Country", "Year", "Count", "Rate", "Source", "Source Type"]   
    return HttpResponse(json.dumps(possible_attributes))

@login_required
def get_suggested_attributes(request):
    print("upload_id = %s" % request.GET.get('upload_id', ''))
    print("attributenumber = %s" % request.GET.get('attributenumber', ''))

    returned_dict = [    {'attribute_name':'Country', 'description':'this is the best option! :)', "format": { "type": "string", "min_length": 4, "max_length": 52 }},
                        {'attribute_name':'Year', 'description':'this is a great option!', "format": { "type": "int", "min": 1995, "max": 2011, "sign": "positive" }},
                        {'attribute_name':'Count', 'description':'this is a good option! ', "format": { "type": "int", "min": 0, "max": 45559, "sign": "non-negative" }},
                        {'attribute_name':'Rate', 'description':'this is an ok option.', "format": { "type": "real", "min": 0.0, "max": 139.1, "sign": "non-negative" }},
                        {'attribute_name':'Source', 'description':'this is a bad option.', "format": { "type": "string", "min_length": 3, "max_length": 28 }},
                        {'attribute_name':'Source Type', 'description':'this is a option...', "format": { "type": "string", "min_length": 2, "max_length": 2, "allowed_values": [ "CJ", "PH" ] }}]
    return HttpResponse(json.dumps(returned_dict))




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
def save_new_object_hierachy_tree(request):
    new_entry = Object_hierachy_tree_history(object_hierachy_tree=request.body, user=request.user)
    new_entry.save()


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
    return render(request, 'tree_of_knowledge_frontend/test_page2.html')

def test_page3(request):
    return render(request, 'tree_of_knowledge_frontend/test_page3.html')





