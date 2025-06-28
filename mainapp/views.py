from rest_framework.views import APIView
from rest_framework.response import Response
from mainapp.serializers import UserSerializer, RegisterSerializer, ProductSerializer, CartGetSerializer, CartSerializer, HomePageImagesSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .models import Cart, Products, Orders, Ratings, HomePageImages
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

TOKEN_EXPIRY_DURATION = 60 * 60 * 60  # Token expiry duration in seconds (1 hour)

class UserLogin(APIView):     #added by venu
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password)
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
    
class UserAuth(APIView):
    def post(self, request):
        data = request.data
        serializers = RegisterSerializer(data=data)
        
        if serializers.is_valid():
            user = serializers.save()
            user.set_password(data['password'])
            user.save()
            token = Token.objects.create(user=user)
            token.created_at = timezone.now()
            token.save()
            return Response({'token': token.key, "user": serializers.data}, status=200)
        elif User.objects.filter(username=data['username']).exists():
            return Response({'message': 'UserName already exists', 'user': serializers.data}, status=400)
        elif User.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists'}, status=400)
        else:
            return Response(serializers.errors, status=400)

    def delete(self, request):
        data = request.data
        user = User.objects.get(username=data["username"])
        if not user.check_password(data["password"]):
            return Response({'error': 'Invalid password'}, status=401)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=200)

class CartGetclass(APIView):
    def post(self, request):
        token = request.data.get("token")
        try:
            user = Token.objects.get(key=token).user 
            cart = Cart.objects.filter(user=user)
            if cart:
                serializers = CartGetSerializer(cart,context={"request": request}, many=True)
                totalPrice=0
                totalQuantity = 0
                for each in serializers.data:
                    totalPrice+=each['product']['price']
                    totalQuantity+=each['quantity']     
                return Response({"data" : serializers.data,"TotalPrice":totalPrice,"TotalQuantity":totalQuantity}, status=200)
            return Response({'message': "cart is empty"}, status=400)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=401)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)   

class Cartclass(APIView):
    
    def post(self, request):
        token = request.data.get("token")
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        try:
            user = Token.objects.get(key=token).user 
            product = Products.objects.get(id=product_id)
            # product_data = ProductSerializer(instance=product)  

            data = {
                "user": user.id,
                "product": product.id,  
                "quantity": quantity
            }
            serializer = CartSerializer(data=data)
            if Cart.objects.filter(product=product.id,user=user.id).exists():                    
                cart = Cart.objects.get(product=product.id,user=user.id)
                print(cart)
                cart.quantity += int(quantity)
                if cart.quantity<=0:
                    cart.delete()
                    return Response({'message': 'item deleted'}, status=201)
                cart.save()
                return Response({'message': 'Quantity increased/dicreased successfully'}, status=201)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Product added to cart successfully'}, status=201)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

    def delete(self, request):
        token = request.data.get("token")
        product_id = request.data.get("product_id")
        try:
            user = Token.objects.get(key=token).user
            if product_id:      
                product = Products.objects.get(id=product_id)
                if Cart.objects.filter(user=user.id, product=product.id).exists():
                    cart = Cart.objects.get(user=user.id, product=product.id)
                    cart.delete()
                return Response({'message': 'Product removed from cart successfully'}, status=200)
             
            if Cart.objects.filter(user=user.id).exists():
                    cart = Cart.objects.filter(user=user.id)
                    cart.delete()
                    return Response({'message': 'cart deleted successfully'}, status=200)
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
                serializer = ProductSerializer(instance=product, context={"request": request})
            else:
                product = Products.objects.all()
                serializer = ProductSerializer(instance=product, context={"request": request}, many=True)
            
            return Response(serializer.data, status=200)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)

   
    def post(self, request):
        try:
            
            if isinstance(request.data, bytes):
                encoding = chardet.detect(request.body)['encoding']
                data = request.data.decode(encoding or 'utf-8', errors='replace')
                print(request.data)
                data = json.loads(data)
                print(data)

            else:
                data = request.data
            category = data.get('pc_category')
            if category:
                productsObj = Products.objects.filter(category=category)
                if productsObj.exists():
                    serializer = ProductSerializer(productsObj,context={"request": request}, many=True)
                    return Response({
                        'message': 'Products filtered by category',
                        'data': serializer.data
                    }, status=200)

            
            serializers = ProductSerializer(data=data, context={"request": request})
            if serializers.is_valid():
                serializers.save()
                return Response({
                    'message': 'Product created successfully',
                    'product': serializers.data
                }, status=201)

            return Response({
                'message': 'Validation error',
                'errors': serializers.errors
            }, status=400)

        except UnicodeDecodeError as e:
            return Response({
                'error': f'Invalid character encoding: {str(e)}'
            }, status=400)
        except json.JSONDecodeError as e:
            return Response({
                'error': f'Invalid JSON format: {str(e)}'
            }, status=400)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=500)

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

class HomeImages(APIView):

    def get(self, request):
        category = request.query_params.get("category")
        try:
            if category:
                images = HomePageImages.objects.filter(category=category)
                serializer = HomePageImagesSerializer(instance=images, many=True, context={"request": request})
                return Response({"data": serializer.data}, status=200)
            else:
                images = HomePageImages.objects.all()
                serializer = HomePageImagesSerializer(instance=images, many=True, context={"request": request})
                return Response({"data": serializer.data}, status=200)
        except HomePageImages.DoesNotExist:
            return Response({"message": "Images not found"}, status=404)
        except Exception as e:
            return Response({'error': str(e)},status=500)
        
    def post(self, request):
        data = request.data
        try :
            serializer = HomePageImagesSerializer(data=data)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':"image uploaded successfully"},status=201)
            return Response({'error': serializer.errors},status=400)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
    def patch(self, request):
        id = request.data.get('id')
        try :
            image = HomePageImages.objects.get(id=id)
            serializer = HomePageImagesSerializer(instance=image,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': "updated successfully"},status=201)
            return Response({'error': serializer.errors},status=400)
        except HomePageImages.DoesNotExist:
            return Response({'message': "image not found"},status=404)
        except Exception as e:
            return Response({'error': str(e)},status=500)