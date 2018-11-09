from django.shortcuts import render
from collection.models import Newsletter_subscriber
from collection.forms import Subscriber_preferencesForm

# Create your views here.
def index(request):
	return render(request, 'index.html')

def landing_page(request):
	return render(request, 'landing_page.html')

def contact(request):
	return render(request, 'contact.html')

def newsletter_subscribers(request):
	newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
	return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})

# def subscriber_page(request, userid):
# 	subscriber = Newsletter_subscriber.objects.get(userid=userid)	
# 	return render (request, 'subscribers/subscriber_page.html', {'subscriber':subscriber})


def subscriber_page(request, userid):
	subscriber = Newsletter_subscriber.objects.get(userid=userid)
	
	is_post_request = False
	if request.method == 'POST':
		is_post_request = True
		form_class = Subscriber_preferencesForm
		form = form_class(data=request.POST, instance=subscriber)
		if form.is_valid():
			form.save()

	return render(request, 'subscribers/subscriber_page.html', {'subscriber':subscriber, 'is_post_request':is_post_request, })
