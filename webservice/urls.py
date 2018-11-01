from django.contrib import admin
from collection import views
from django.conf.urls import include, url
from django.urls import path




urlpatterns = [
	url(r'^$', views.index, name='home'),
	url(r'^subscribers/$', views.newsletter_subscribers, name='subscribers'),
	# url(r'^user$/(?P<slug>[-\w]+)/$', views.user_page, name='user_page'),
	path('admin/', admin.site.urls),
	# url(r'^admin/$', admin.site.urls),
]



# # Alternative ---------------------------------------------------------------------
# 
# from django.urls import path
# 
# urlpatterns = [
# 	path('', views.index, name='home'),
# 	path('subscribers', views.newsletter_subscribers, name='subscribers'),
#    path('admin/', admin.site.urls),
# ]
# # -----------------------------------------------------------------------------------