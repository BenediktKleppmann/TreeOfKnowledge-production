from django.db import models


class Newsletter_subscriber(models.Model):
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=255)


class User(models.Model):
	email = models.EmailField(unique=True)
	username = models.CharField(max_length=255, unique=True)
	password = models.CharField(max_length=255)
