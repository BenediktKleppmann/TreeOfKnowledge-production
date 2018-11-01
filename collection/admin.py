from django.contrib import admin

# import the models
from collection.models import Newsletter_subscriber



# register the models
admin.site.register(Newsletter_subscriber)