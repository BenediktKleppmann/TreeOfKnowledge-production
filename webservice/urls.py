from django.contrib import admin
from django.urls import path
from collection import views
# from django.conf.urls import include, url

urlpatterns = [
	path('', views.index, name='home'),
	# url(r'^$','collection.views.index', name='home'),
    path('admin/', admin.site.urls),
]
