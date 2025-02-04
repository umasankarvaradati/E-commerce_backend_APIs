from mainapp.views import UserAuth, products,Cartclass
from django.urls import path

urlpatterns = [
    path('auth/', UserAuth.as_view()),
    path('products/', products.as_view()),
    path('cart/',Cartclass.as_view())
]
