from django.contrib import admin
from django.contrib.auth.models import User
from .models import Products,Cart,Ratings,Orders

admin.site.register(Cart)
admin.site.register(Products)
admin.site.register(Ratings)
admin.site.register(Orders)