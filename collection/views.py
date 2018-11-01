from django.shortcuts import render
from collection.models import Newsletter_subscriber

# Create your views here.
def index(request):
	return render(request, 'index.html')

def newsletter_subscribers(request):
	newsletter_subscribers = Newsletter_subscriber.objects.all().order_by('email')
	return render(request, 'newsletter_subscribers.html', {'newsletter_subscribers': newsletter_subscribers,})