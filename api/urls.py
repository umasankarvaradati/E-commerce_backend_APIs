from mainapp.views import UserAuth, products,Cartclass, UserLogin, CartGetclass, HomeImages
from django.urls import path

urlpatterns = [
    path('auth/', UserAuth.as_view()),
    path('products/', products.as_view()),
    path('cart/',Cartclass.as_view()),
    path('login/',UserLogin.as_view()),
    path('getcart/',CartGetclass.as_view()),
    path('homeimages/',HomeImages.as_view()),
]
