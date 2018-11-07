from django.contrib import admin

# import the models
from collection.models import Newsletter_subscriber

# automated email_hash creation for Newsletter subscribers
class Newsletter_subscriberAdmin(admin.ModelAdmin):
	model = Newsletter_subscriber
	list_display = ('email', 'userid', 'first_name','is_templar', 'is_alchemist', 'is_archivist', 'created', 'updated')
	# prepopulated_fields = {'userid': ('email',), 'created': ('email',),'updated': ('email',),}
	
	

# register the models
admin.site.register(Newsletter_subscriber, Newsletter_subscriberAdmin)