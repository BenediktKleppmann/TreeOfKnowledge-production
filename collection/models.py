from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import datetime
import hashlib


class Newsletter_subscriber(models.Model):
    email = models.EmailField(unique=True)
    userid = models.IntegerField(editable=False, unique=True)
    first_name = models.CharField(max_length=255)
    is_templar = models.BooleanField(default=False)
    is_alchemist = models.BooleanField(default=False)
    is_scholar = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    def save(self):
        # set the userid to be the md5-hash of the email
        email_string = self.email.encode('utf-8')
        self.userid = int(hashlib.sha1(email_string).hexdigest(), 16) % (10 ** 8)

        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Newsletter_subscriber, self).save()





# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     created = models.DateTimeField(editable=False)
#     updated = models.DateTimeField(editable=False)
#     def save(self):
#         if not self.id:
#             self.created = datetime.datetime.today()
#         self.updated = datetime.datetime.today()
#         super(Simulation_model, self).save()







class Uploaded_dataset(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    sep = models.CharField(max_length=3, blank=True, null=True)
    encoding = models.CharField(max_length=10, blank=True, null=True)
    quotechar = models.CharField(max_length=1, blank=True, null=True)
    escapechar = models.CharField(max_length=1, blank=True, null=True)
    na_values = models.TextField(blank=True, null=True)
    skiprows = models.CharField(max_length=20, blank=True, null=True)
    header = models.CharField(max_length=10, blank=True, null=True)
    data_table_json = models.TextField()
    # upload_data2
    data_source = models.TextField(null=True)
    data_generation_date = models.DateField(null=True)
    correctness_of_data = models.IntegerField(null=True)
    # upload_data3
    object_type = models.TextField()
    entire_objectInfoHTMLString = models.TextField(null=True)
    # upload_data4
    attribute1 = models.TextField(null=True)
    operator1 = models.TextField(null=True)
    value1 = models.TextField(null=True)
    start_date1 = models.DateField(null=True)
    end_date1 = models.DateField(null=True)
    attribute2 = models.TextField(null=True)
    operator2 = models.TextField(null=True)
    value2 = models.TextField(null=True)
    start_date2 = models.DateField(null=True)
    end_date2 = models.DateField(null=True)
    attribute3 = models.TextField(null=True)
    operator3 = models.TextField(null=True)
    value3 = models.TextField(null=True)
    start_date3 = models.DateField(null=True)
    end_date3 = models.DateField(null=True)
    attribute4 = models.TextField(null=True)
    operator4 = models.TextField(null=True)
    value4 = models.TextField(null=True)
    start_date4 = models.DateField(null=True)
    end_date4 = models.DateField(null=True)
    attribute5 = models.TextField(null=True)
    operator5 = models.TextField(null=True)
    value5 = models.TextField(null=True)
    start_date5 = models.DateField(null=True)
    end_date5 = models.DateField(null=True)
    attribute6 = models.TextField(null=True)
    operator6 = models.TextField(null=True)
    value6 = models.TextField(null=True)
    start_date6 = models.DateField(null=True)
    end_date6 = models.DateField(null=True)
    attribute7 = models.TextField(null=True)
    operator7 = models.TextField(null=True)
    value7 = models.TextField(null=True)
    start_date7 = models.DateField(null=True)
    end_date7 = models.DateField(null=True)
    attribute8 = models.TextField(null=True)
    operator8 = models.TextField(null=True)
    value8 = models.TextField(null=True)
    start_date8 = models.DateField(null=True)
    end_date8 = models.DateField(null=True)
    attribute9 = models.TextField(null=True)
    operator9 = models.TextField(null=True)
    value9 = models.TextField(null=True)
    start_date9 = models.DateField(null=True)
    end_date9 = models.DateField(null=True)
    attribute10 = models.TextField(null=True)
    operator10 = models.TextField(null=True)
    value10 = models.TextField(null=True)
    start_date10 = models.DateField(null=True)
    end_date10 = models.DateField(null=True)
    attribute11 = models.TextField(null=True)
    operator11 = models.TextField(null=True)
    value11 = models.TextField(null=True)
    start_date11 = models.DateField(null=True)
    end_date11 = models.DateField(null=True)
    attribute12 = models.TextField(null=True)
    operator12 = models.TextField(null=True)
    value12 = models.TextField(null=True)
    start_date12 = models.DateField(null=True)
    end_date12 = models.DateField(null=True)
    attribute13 = models.TextField(null=True)
    operator13 = models.TextField(null=True)
    value13 = models.TextField(null=True)
    start_date13 = models.DateField(null=True)
    end_date13 = models.DateField(null=True)
    attribute14 = models.TextField(null=True)
    operator14 = models.TextField(null=True)
    value14 = models.TextField(null=True)
    start_date14 = models.DateField(null=True)
    end_date14 = models.DateField(null=True)
    attribute15 = models.TextField(null=True)
    operator15 = models.TextField(null=True)
    value15 = models.TextField(null=True)
    start_date15 = models.DateField(null=True)
    end_date15 = models.DateField(null=True)
    attribute16 = models.TextField(null=True)
    operator16 = models.TextField(null=True)
    value16 = models.TextField(null=True)
    start_date16 = models.DateField(null=True)
    end_date16 = models.DateField(null=True)
    attribute17 = models.TextField(null=True)
    operator17 = models.TextField(null=True)
    value17 = models.TextField(null=True)
    start_date17 = models.DateField(null=True)
    end_date17 = models.DateField(null=True)
    attribute18 = models.TextField(null=True)
    operator18 = models.TextField(null=True)
    value18 = models.TextField(null=True)
    start_date18 = models.DateField(null=True)
    end_date18 = models.DateField(null=True)
	# upload_data6
    valid_times = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Uploaded_dataset, self).save()


class Object_hierachy_tree_history(models.Model):
    object_hierachy_tree = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    timestamp = models.DateTimeField(editable=False)
    def save(self):
        self.timestamp = datetime.datetime.today()
        super(Object_hierachy_tree_history, self).save()

class Object_types(models.Model):
	id = models.TextField(primary_key=True)
	parent = models.TextField()
	name = models.TextField()
	li_attr = models.TextField(null=True)
	a_attr = models.TextField(null=True)

class Attribute(models.Model):
	attribute_name = models.TextField()
	format_specification = models.TextField()
	first_applicable_object = models.ForeignKey(Object_types, on_delete=models.SET_NULL, blank=True, null=True,)


class Object_properties(models.Model):
	first_applicable_object = models.ForeignKey(Object_types, on_delete=models.SET_NULL, blank=True, null=True,)
	attribute =  models.ForeignKey(Attribute, on_delete=models.SET_NULL, blank=True, null=True,)
	operation = models.CharField(max_length=2)
	value = models.TextField()



class Simulation_model(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    # is_private  = models.BooleanField(default=False)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Simulation_model, self).save()


class Meta_data_constaint(models.Model):
	simulation_model = models.ForeignKey(Simulation_model, on_delete=models.SET_NULL, blank=True, null=True,)
	attribute =  models.ForeignKey(Attribute, on_delete=models.SET_NULL, blank=True, null=True,)
	operation = models.CharField(max_length=2)
	value = models.TextField()


# class Data_points(models.Model):
# 	object_type = models.ForeignKey(Attributes, on_delete=models.SET_NULL, blank=True, null=True,)
# 	object_id = models.IntegerField()
# 	attribute = models.ForeignKey(Attributes, on_delete=models.SET_NULL, blank=True, null=True,)
# 	valid_time_start = models.IntegerField()
# 	valid_time_end = models.IntegerField()
# 	data_quality = models.IntegerField()



