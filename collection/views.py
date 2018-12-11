from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3
from django.template.defaultfilters import slugify
from collection.functions import upload_data
from collection.functions import get_from_db
from django.http import HttpResponse
import json


# ===== THE WEBSITE ===================================================================
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


# ===== ADMIN PAGES ===================================================================

def newsletter_subscribers(request):
    newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
    return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})



# ===== THE TOOL ===================================================================
@login_required
def main_menu(request):
    models = Simulation_model.objects.all().order_by('id') 
    return render(request, 'tree_of_knowledge_frontend/main_menu.html', {'models': models})



# ==============================================================


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
                upload_id = upload_data.save_data_and_suggestions(data_file, request.user)
                return redirect('upload_data2', upload_id=upload_id)

        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})
    else:
        form1 = UploadFileForm()
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})





@login_required
def upload_data2(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        form1 = UploadFileForm()
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})

    if request.method == 'POST':        
        form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form2.save()
            return redirect('upload_data3', upload_id=upload_id)

    object_hierachy_tree = get_from_db.get_object_hierachy_tree()
    return render(request, 'tree_of_knowledge_frontend/upload_data2.html', {'uploaded_dataset': uploaded_dataset, 'object_hierachy_tree':object_hierachy_tree, 'errors': errors})

                

@login_required
def upload_data3(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        form1 = UploadFileForm()
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})

    
    if request.method == 'POST':
        form3 = Uploaded_datasetForm3(data=request.POST, instance=uploaded_dataset)
        if not form3.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form3.save()
            return redirect('main_menu')

    
    return render(request, 'tree_of_knowledge_frontend/upload_data3.html', {'uploaded_dataset': uploaded_dataset, 'errors': errors})



@login_required
def get_suggested_attributes(request):
    print("upload_id = %s" % request.GET.get('upload_id', ''))
    print("attributenumber = %s" % request.GET.get('attributenumber', ''))

    returned_dict = [    {'attribute_name':'option 1', 'number_of_conflicting_values':0, 'conflicting_rows':[], 'description':'this is the best option! :)', "format": { "type": "string", "min_length": 3, "max_length": 11, "max_nulls": 0 }},
                        {'attribute_name':'option 2', 'number_of_conflicting_values':1, 'conflicting_rows':[5], 'description':'this is a great option!', "format": { "type": "date", "min": "1954-04-26 00:00:00", "max": "2009-12-17 00:00:00", "max_nulls": 0 }},
                        {'attribute_name':'option 3', 'number_of_conflicting_values':4, 'conflicting_rows':[2,5,9,24], 'description':'this is a good option! ', "format": { "type": "string", "min_length": 7, "max_length": 8, "max_nulls": 0, "allowed_values": [ "sleeping", "working" ] }},
                        {'attribute_name':'option 4', 'number_of_conflicting_values':7, 'conflicting_rows':[1,5,9,12,27, 28, 29], 'description':'this is an ok option.', "format": { "type": "string", "min_length": 4, "max_length": 52, "max_nulls": 0 }},
                        {'attribute_name':'option 5', 'number_of_conflicting_values':9, 'conflicting_rows':[3,5,6,18,23,25,29,30,31], 'description':'this is a bad option.', "format": { "type": "int", "min": 1995, "max": 2011, "sign": "positive", "max_nulls": 0 }},
                        {'attribute_name':'option 6', 'number_of_conflicting_values':15, 'conflicting_rows':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 'description':'this is a option...', "format": { "type": "int", "min": 0, "max": 45559, "sign": "non-negative", "max_nulls": 0 }}]
    return HttpResponse(json.dumps(returned_dict))


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


# =======================================================================================
def test_page(request):
    return render(request, 'tree_of_knowledge_frontend/test_page.html')