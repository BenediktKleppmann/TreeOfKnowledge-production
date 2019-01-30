# from registration.backends.simple.views import RegistrationView
from collection.backends import TOKRegistrationView
from django.contrib import admin
from collection import views
from django.views.generic import RedirectView
from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import (
    password_reset,
    password_reset_done,
    password_reset_confirm,
    password_reset_complete
)




urlpatterns = [
    # The Website
    url(r'^$', views.landing_page, name='landing_page'),
    url(r'^about/$', views.about, name='about'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^subscriber/(?P<userid>[-\d]+)/$', views.subscriber_page, name='user_page'),

    # Registration
    url(r'^accounts/password/reset/$', password_reset, {'template_name': 'registration/password_reset_form.html'}, name='password_reset'),
    url(r'^accounts/password/reset/done/$', password_reset_done, {'template_name': 'registration/password_reset_done.html'}, name='password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, {'template_name': 'registration/password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^accounts/password/done/$', password_reset_complete, {'template_name': 'registration/password_reset_complete.html'}, name='password_reset_complete'),
    # url(r'^accounts/register/$', RegistrationView.as_view(),name='registration_register'),
    url(r'^accounts/register/$', TOKRegistrationView.as_view(),name='registration_register'),
    url(r'^accounts/register/complete/$', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^', include('django.contrib.auth.urls')),


	# ==================================================
    # TOOL  
    # ==================================================
    url(r'^tool/main_menu/$', views.main_menu, name='main_menu'),

    # Upload data
    url(r'^tool/upload_data1/$', views.upload_data1_new, name='upload_data1_new'),
    url(r'^tool/upload_data1/(?P<upload_id>[-\d]+)/$', views.upload_data1, name='upload_data1'),
    url(r'^tool/upload_data2/(?P<upload_id>[-\d]+)/$', views.upload_data2, name='upload_data2'),
    url(r'^tool/upload_data3/(?P<upload_id>[-\d]+)/$', views.upload_data3, name='upload_data3'),
    url(r'^tool/upload_data4/(?P<upload_id>[-\d]+)/$', views.upload_data4, name='upload_data4'),
    url(r'^tool/upload_data5/(?P<upload_id>[-\d]+)/$', views.upload_data5, name='upload_data5'),
    url(r'^tool/upload_data6/(?P<upload_id>[-\d]+)/$', views.upload_data6, name='upload_data6'),
    url(r'^tool/upload_data_success/(?P<new_model_id>[-\d]+)/$', views.upload_data_success, name='upload_data_success'),

	# Helper Functions
    url(r'^tool/upload_data5__edit_column/$', views.upload_data5__edit_column, name='upload_data5__edit_column'),
    url(r'^tool/upload_data5__get_columns_format_violations/$', views.upload_data5__get_columns_format_violations, name='upload_data5__get_columns_format_violations'),
    url(r'^tool/upload_data5__suggest_attribute_format/$', views.upload_data5__suggest_attribute_format, name='upload_data5__suggest_attribute_format'),
    url(r'^tool/check_single_fact_format/$', views.check_single_fact_format, name='check_single_fact_format'),    
    url(r'^tool/get_possible_attributes/$', views.get_possible_attributes, name='get_possible_attributes'),
    url(r'^tool/get_suggested_attributes/$', views.get_suggested_attributes, name='get_suggested_attributes'),
    url(r'^tool/save_new_object_hierachy_tree/$', views.save_new_object_hierachy_tree, name='save_new_object_hierachy_tree'),

    # Simulation
    url(r'^tool/edit_model/$', views.new_model, name='new_model'),
    url(r'^tool/edit_model/(?P<id>[-\d]+)/$', views.edit_model, name='edit_model'),
    url(r'^main_menu/$', RedirectView.as_view(pattern_name='main_menu')),
    url(r'^edit_model/$', RedirectView.as_view(pattern_name='edit_model')),


    # Admin Pages
    url(r'^subscribers/$', views.newsletter_subscribers, name='subscribers'),
	url(r'^clear_database/$', views.clear_database, name='clear_database'),
    url(r'^populate_database/$', views.populate_database, name='populate_database'),
    url(r'^test_page1/$', views.test_page1, name='test_page1'),
    url(r'^test_page2/$', views.test_page2, name='test_page2'),
    url(r'^test_page3/$', views.test_page3, name='test_page3'),
    path('admin/', admin.site.urls),


]



# # Alternative ---------------------------------------------------------------------
# 
# from django.urls import path
# 
# urlpatterns = [
#     path('', views.index, name='home'),
#     path('subscribers', views.newsletter_subscribers, name='subscribers'),
#    path('admin/', admin.site.urls),
# ]
# # -----------------------------------------------------------------------------------