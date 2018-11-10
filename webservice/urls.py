from django.contrib import admin
from collection import views
from django.conf.urls import include, url
from django.urls import path




urlpatterns = [
	url(r'^$', views.landing_page, name='landing_page'),
	url(r'^about/$', views.about, name='about'),
	url(r'^subscribe/$', views.subscribe, name='subscribe'),
	url(r'^contact/$', views.contact, name='contact'),
	url(r'^subscribers/$', views.newsletter_subscribers, name='subscribers'),
	# url(r'^subscriber_home'),
	url(r'^subscriber/(?P<userid>[-\d]+)/$', views.subscriber_page, name='user_page'),
	path('admin/', admin.site.urls),
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