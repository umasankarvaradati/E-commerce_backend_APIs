from django.db import models
from django.contrib.auth.models import User

class Products(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    stock = models.IntegerField()

class Cart(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    quantity = models.IntegerField()

class Ratings(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    images = models.ImageField(upload_to='products/')
    rating = models.IntegerField()
    review = models.TextField(max_length=150)

class Orders(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    date = models.DateField()

class HomePageImages(models.Model):
    id = models.AutoField(primary_key=True,unique=True)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=100)
