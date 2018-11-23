from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber, Simulation_model
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm, Simulation_modelForm
from django.template.defaultfilters import slugify


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


@login_required
def main_menu2(request):
	models = Simulation_model.objects.all().order_by('id') 
	return render(request, 'tree_of_knowledge_frontend/main_menu2.html', {'models': models})


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


