from django.forms import ModelForm
from collection.models import Newsletter_subscriber

class SubscriberForm(ModelForm):
	class Meta:
		model = Newsletter_subscriber
		fields = ('email',  'first_name', 'is_templar', 'is_alchemist', 'is_scholar',)