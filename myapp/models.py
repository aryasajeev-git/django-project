from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Usersprofile(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    phone_no=models.IntegerField()
    gender=models.CharField(max_length=50)
    photo=models.CharField(max_length=50)
    AUTHUSER=models.OneToOneField(User,on_delete=models.CASCADE)

class Document(models.Model):
    FileName=models.CharField(max_length=100)
    File=models.CharField(max_length=200)
    Type=models.CharField(max_length=50)
    User=models.ForeignKey(Usersprofile,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.FileName} ({self.Type})"