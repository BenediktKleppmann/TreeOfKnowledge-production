from django.db import models
import datetime


class Newsletter_subscriber(models.Model):
	email = models.EmailField(unique=True)
	userid = models.IntegerField(editable=False, unique=True)
	first_name = models.CharField(max_length=255)
	is_templar = models.BooleanField(default=False)
	is_alchemist = models.BooleanField(default=False)
	is_archivist = models.BooleanField(default=False)
	created = models.DateTimeField(editable=False)
	updated = models.DateTimeField(editable=False)

	def save(self):
		self.userid = hash(self.email)
		if not self.id:
			self.created = datetime.datetime.today()
		self.updated = datetime.datetime.today()
		super(Newsletter_subscriber, self).save()

	


class User(models.Model):
	email = models.EmailField(unique=True)
	username = models.CharField(max_length=255, unique=True)
	password = models.CharField(max_length=255)
