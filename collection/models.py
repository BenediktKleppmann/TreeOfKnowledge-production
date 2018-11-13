from django.db import models
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



class User(models.Model):
	email = models.EmailField(unique=True)
	username = models.CharField(max_length=255, unique=True)
	password = models.CharField(max_length=255)
	created = models.DateTimeField(editable=False)
	updated = models.DateTimeField(editable=False)
	def save(self):
		if not self.id:
			self.created = datetime.datetime.today()
		self.updated = datetime.datetime.today()
		super(Simulation_model, self).save()


class Simulation_model(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True)
	description = models.TextField()
	specification = JSONField()
	created = models.DateTimeField(editable=False)
	updated = models.DateTimeField(editable=False)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
	def save(self):
		if not self.id:
			self.created = datetime.datetime.today()
		self.updated = datetime.datetime.today()
		super(Simulation_model, self).save()



class Uploaded_dataset(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True)
	description = models.TextField()
	specification = JSONField()
	uploaded = models.DateTimeField(editable=False)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
	def save(self):
		self.uploaded = datetime.datetime.today()
		super(Uploaded_dataset, self).save()




