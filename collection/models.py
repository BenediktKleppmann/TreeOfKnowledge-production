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


class Simulation_model(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    specification = models.TextField()
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    # is_private  = models.BooleanField(default=False)
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Simulation_model, self).save()




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
    attribute2 = models.TextField(null=True)
    operator2 = models.TextField(null=True)
    value2 = models.TextField(null=True)
    attribute3 = models.TextField(null=True)
    operator3 = models.TextField(null=True)
    value3 = models.TextField(null=True)
    attribute4 = models.TextField(null=True)
    operator4 = models.TextField(null=True)
    value4 = models.TextField(null=True)
    attribute5 = models.TextField(null=True)
    operator5 = models.TextField(null=True)
    value5 = models.TextField(null=True)
    attribute6 = models.TextField(null=True)
    operator6 = models.TextField(null=True)
    value6 = models.TextField(null=True)
    attribute7 = models.TextField(null=True)
    operator7 = models.TextField(null=True)
    value7 = models.TextField(null=True)
    attribute8 = models.TextField(null=True)
    operator8 = models.TextField(null=True)
    value8 = models.TextField(null=True)
    attribute9 = models.TextField(null=True)
    operator9 = models.TextField(null=True)
    value9 = models.TextField(null=True)
    attribute10 = models.TextField(null=True)
    operator10 = models.TextField(null=True)
    value10 = models.TextField(null=True)
    attribute11 = models.TextField(null=True)
    operator11 = models.TextField(null=True)
    value11 = models.TextField(null=True)
    attribute12 = models.TextField(null=True)
    operator12 = models.TextField(null=True)
    value12 = models.TextField(null=True)
    attribute13 = models.TextField(null=True)
    operator13 = models.TextField(null=True)
    value13 = models.TextField(null=True)
    attribute14 = models.TextField(null=True)
    operator14 = models.TextField(null=True)
    value14 = models.TextField(null=True)
    attribute15 = models.TextField(null=True)
    operator15 = models.TextField(null=True)
    value15 = models.TextField(null=True)
    attribute16 = models.TextField(null=True)
    operator16 = models.TextField(null=True)
    value16 = models.TextField(null=True)
    attribute17 = models.TextField(null=True)
    operator17 = models.TextField(null=True)
    value17 = models.TextField(null=True)
    attribute18 = models.TextField(null=True)
    operator18 = models.TextField(null=True)
    value18 = models.TextField(null=True)
	# upload_data6
    context_specification = models.TextField()
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

class Object_hierachy_tree(models.Model):
	id = models.TextField(primary_key=True)
	parent = models.TextField()
	text = models.TextField()
	li_attr = models.TextField(null=True)
	a_attr = models.TextField(null=True)


