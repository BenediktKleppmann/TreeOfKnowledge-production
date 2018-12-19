from django.contrib import admin

# import the models
from collection.models import Newsletter_subscriber
from collection.models import Simulation_model
from collection.models import Uploaded_dataset


# automated email_hash creation for Newsletter subscribers
class Newsletter_subscriberAdmin(admin.ModelAdmin):
	model = Newsletter_subscriber
	list_display = ('email', 'userid', 'first_name','is_templar', 'is_alchemist', 'is_scholar', 'created', 'updated')
	# prepopulated_fields = {'userid': ('email',), 'created': ('email',),'updated': ('email',),}



class Uploaded_datasetAdmin(admin.ModelAdmin):
	model = Simulation_model
	list_display = ('file_name', 'file_path', 'sep', 'encoding', 'quotechar', 'escapechar', 'na_values', 'skiprows', 'header', 'created', 'updated', 'user')




# register the models
admin.site.register(Newsletter_subscriber, Newsletter_subscriberAdmin)
admin.site.register(Simulation_model)
admin.site.register(Uploaded_dataset, Uploaded_datasetAdmin)