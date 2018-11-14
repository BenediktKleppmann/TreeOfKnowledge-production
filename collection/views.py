from django.shortcuts import render, redirect
from collection.models import Newsletter_subscriber
from collection.forms import Subscriber_preferencesForm, Subscriber_registrationForm

# Create your views here.
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
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print(form.cleaned_data)
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			return render(request, 'subscribe.html', {'error_occured': True,})

	else:
		return render(request, 'subscribe.html', {'error_occured': False,})




def contact(request):
	return render(request, 'contact.html')


def main_menu(request):
	return render(request, 'tree_of_knowledge_frontend/main_menu.html')



def newsletter_subscribers(request):
	newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
	return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})

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
