from django.db import models
from django.contrib.auth.models import AbstractUser

class Permission(models.Model):
	name = models.CharField(max_length=200)


class Role(models.Model):
	# Role will have MULTIPLE Permissions
	name = models.CharField(max_length=200)
	# many-to-many, so need another table; this is automatically done when we create migrations, and django will make another table 
	# python manage.py makemigrations => python manage.py migrate
	permissions = models.ManyToManyField(Permission)



class User(AbstractUser):
	print(AbstractUser)
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	email = models.CharField(max_length=200, unique=True)
	password = models.CharField(max_length=200)
	# Foregin key relation between the user and the role: ONE USER, ONE ROLE
	role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
	username = None

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
