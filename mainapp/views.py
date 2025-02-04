from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from mainapp.serializers import UserSerializer, RegisterSerializer, ProductSerializer, OrdersSerializer, CartSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .models import Cart, Products, Orders, Ratings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

TOKEN_EXPIRY_DURATION = 60 * 60 *60  # Token expiry duration in seconds (1 hour)

class UserAuth(APIView):
    def get(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'message': 'Invalid username'}, status=401)

        if not user.check_password(password):
            return Response({'error': 'Invalid password'}, status=401) 
        
        token, created = Token.objects.get_or_create(user=user)

        if created:
            token.created_at = timezone.now()
            token.save()

        serializers = UserSerializer(user)
        return Response({'message': 'User authenticated successfully', 'token': token.key, 'user': serializers.data}, status=200)

    def post(self, request):
        data = request.data
        serializers = RegisterSerializer(data=data)
        if serializers.is_valid():
            user = serializers.save()
            user.set_password(data['password'])
            user.save()
            token = Token.objects.create(user=user)
            token.created_at = timezone.now()
            print()
            token.save()
            return Response({'token': token.key, "user": serializers.data}, status=200)
        return Response({'message': serializers.errors, 'user': serializers.data}, status=400)

    def delete(self, request):
        data = request.data
        user = User.objects.get(username=data["username"])
        if not user.check_password(data["password"]):
            return Response({'error': 'Invalid password'}, status=401)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=200)
    

class Cartclass(APIView):
    def get(self, request):
        token = request.data.get("token")
        try:
            user = Token.objects.get(key=token).user  
            cart = Cart.objects.filter(user=user)
            if cart:
                serializers = CartSerializer(cart, many=True)
                return Response({'message': 'added to cart', 'cart': serializers.data}, status=200)
            return Response({'message': "cart is empty"}, status=401)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=401)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        token = request.data.get("token")
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        try:
            user = Token.objects.get(key=token).user 
            product = Products.objects.get(id=product_id)
            data = {
                "user": user.id,
                "product": product.id, 
                "quantity": quantity
            }
            serializer = CartSerializer(data=data)
            if Cart.objects.filter(product=product.id).exists():
                cart = Cart.objects.get(product=product.id)
                cart.quantity += int(quantity)
                cart.save()
                return Response({'message': 'Quantity increased successfully'}, status=201)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Product added to cart successfully'}, status=201)
        except User.DoesNotExist:
            return Response({'error': 'User not found', 'message': serializer.errors}, status=404)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found', 'message': serializer.errors}, status=404)

        return Response({'message': serializer.errors, "data": serializer.data}, status=400)

    def delete(self, request):
        token = request.data.get("token")
        product_id = request.data.get("product_id")
        try:
            user = Token.objects.get(key=token).user       
            product = Products.objects.get(id=product_id)
            if Cart.objects.filter(user=user.id, product=product.id).exists():
                cart = Cart.objects.get(user=user.id, product=product.id)
                cart.delete()
                return Response({'message': 'Product removed from cart successfully'}, status=200)
            return Response({'error': 'Product not found in cart'}, status=404)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

class products(APIView):
    def get(self, request):
        id = request.data.get("id")
        
        try:
            if id:
                product = Products.objects.get(id=id)
                serializer = ProductSerializer(instance=product)
            else:
                product = Products.objects.all()
                serializer = ProductSerializer(instance=product, many=True)
            
            return Response(serializer.data, status=200)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)

    def post(self, request):
        data = request.data
        serializers = ProductSerializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message': 'Product created successfully', 'product': serializers.data}, status=200)
        return Response({'message': serializers.errors, 'product': serializers.data}, status=400)

    def delete(self, request):
        id = request.data.get("id")
        try:
            product = Products.objects.get(id=id)
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=200)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)

    def patch(self, request):
        id = request.data.get("id")
        try:
            product = Products.objects.get(id=id)
            serializers = ProductSerializer(instance=product, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response({'message': 'Product updated successfully'}, status=200)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)
