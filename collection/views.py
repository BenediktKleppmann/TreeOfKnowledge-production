from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model, Uploaded_dataset
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm, UploadFileForm, Uploaded_datasetForm2, Uploaded_datasetForm3
from django.template.defaultfilters import slugify
from collection.functions import upload_data


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
            return redirect('/subscriber/' + str(subscriber.userid))
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
    print("!!!!!!!!!Test 1")
    if request.method == 'POST':
        print("!!!!!!!!!Test 2")
        form1 = UploadFileForm(request.POST, request.FILES)
        print("!!!!!!!!!Test 3")
        if not form1.is_valid():
            print("!!!!!!!!!Test 4")
            errors.append("Error: Form not valid.")
        else:
            print("!!!!!!!!!Test 5")
            data_file = request.FILES['file']
            print("!!!!!!!!!Test 6")
            if data_file.name[-4:] !=".csv":
                print("!!!!!!!!!Test 7")
                errors.append("Error: Uploaded file is not a csv-file.")
            else:
                print("!!!!!!!!!Test 8")
                upload_id = upload_data.save_data_and_suggestions(data_file, request.user)
                print('/tool/upload_data2/' + str(upload_id))
                return redirect('/tool/upload_data2/' + str(upload_id))

        print("!!!!!!!!!Test 9")
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})
    else:
        print("!!!!!!!!!Test 10")
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


    form2 = Uploaded_datasetForm2(data=request.POST, instance=uploaded_dataset)
    if request.method == 'POST':        
        if not form2.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form2.save()
            return redirect('/tool/upload_data3/' + str(upload_id))

    
    return render(request, 'tree_of_knowledge_frontend/upload_data2.html', {'form2': form2, 'errors': errors})



@login_required
def upload_data3(request, upload_id):
    errors = []
    # if the upload_id was wrong, send the user back to the first page
    uploaded_dataset = Uploaded_dataset.objects.get(id=upload_id, user=request.user)
    if uploaded_dataset is None:
        errors.append('Error: %s is not a valid upload_id' % str(upload_id))
        form1 = UploadFileForm()
        return render(request, 'tree_of_knowledge_frontend/upload_data1.html', {'form1': form1, 'errors': errors})

    form3 = Uploaded_datasetForm3(data=request.POST, instance=uploaded_dataset)
    if request.method == 'POST':
        if not form3.is_valid():
            errors.append('Error: the form is not valid.')
        else:
            form3.save()
            return redirect('tool/main_menu/')

    
    return render(request, 'tree_of_knowledge_frontend/upload_data3.html', {'form3': form3, 'errors': errors})




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


