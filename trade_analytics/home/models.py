from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserBase(models.Model):
    User = models.ManyToManyField(User)
    class Meta:
        abstract=True
