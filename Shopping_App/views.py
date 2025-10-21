from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.shortcuts import get_object_or_404
from decimal import Decimal
import uuid
import requests
import paypalrestsdk
from django.conf import settings

from .models import Products, Cart, CartItem, Transaction
from .serializers import (
    ProductsSerializer,
    DetailProductSerializer,
    CartItemSerializer,
    CartSerializer,
    SimpleCartSerializer,
    UserSerializer,
    CustomUsersSerializer,
    ProductsPagination,
)

BASE_URL = settings.REACT_BASE_URL

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET_KEY
})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_Products(request):
    products = Products.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    serializer = ProductsSerializer(products, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_product_detail(request, slug):
    product = get_object_or_404(Products, slug=slug)
    serializer = DetailProductSerializer(product)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([AllowAny])
def add_item(request):
    try:
        cart_code = request.data.get("cart_code")
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not cart_code or not product_id:
            return Response({"error": "cart_code and product_id are required."}, status=400)
        if quantity < 1:
            return Response({"error": "Quantity must be at least 1."}, status=400)

        product = get_object_or_404(Products, id=product_id)
        cart, _ = Cart.objects.get_or_create(cart_code=cart_code)

        # Attach user if authenticated
        if request.user.is_authenticated and not cart.user:
            cart.user = request.user
            cart.save()

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity if created else cart_item.quantity + quantity
        cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response({
            "message": "Item added to cart.",
            "cart": cart_serializer.data
        }, status=201)

    except ValueError:
        return Response({"error": "Quantity must be a number."}, status=400)
    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)

@api_view(["GET"])
@permission_classes([AllowAny])
def check_product_in_cart(request):
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")

    if not cart_code or not product_id:
        return Response({"error": "Missing cart_code or product_id"}, status=400)

    try:
        cart = Cart.objects.get(cart_code=cart_code, paid=False)
        product = Products.objects.get(id=product_id)
        exists = CartItem.objects.filter(cart=cart, product=product).exists()
        return Response({"exists": exists})
    except:
        return Response({"exists": False})

@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart_stat(request):
    cart_code = request.query_params.get("cart_code")
    if not cart_code:
        return Response({"error": "cart_code is required."}, status=400)

    cart = Cart.objects.filter(cart_code=cart_code, paid=False).first()
    if not cart:
        return Response({"error": "Cart not found or already paid."}, status=404)

    serializer = SimpleCartSerializer(cart)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart(request):
    cart_code = request.query_params.get("cart_code")
    if not cart_code:
        return Response({"error": "cart_code is required."}, status=400)

    try:
        cart = Cart.objects.get(cart_code=cart_code, paid=False)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=404)

@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_quantity(request):
    try:
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            return Response({"error": "Quantity must be at least 1."}, status=400)

        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response({"data": serializer.data, "message": "Cart item updated successfully"})
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_cartitem(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_username(request):
    return Response({"username": request.user.username})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    serializer = CustomUsersSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "User created successfully", 
            "user": CustomUsersSerializer(user).data
        }, status=201)
    return Response({"error": serializer.errors}, status=400)

class ProductsListView(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    pagination_class = ProductsPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category']

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    try:
        user = request.user
        cart_code = request.data.get("cart_code")
        if not cart_code:
            return Response({"error": "cart_code is required."}, status=400)

        cart = get_object_or_404(Cart, cart_code=cart_code)

        subtotal = sum(item.quantity * item.product.price for item in cart.items.all())
        tax = Decimal('1000.00')
        total = subtotal + tax
        currency = "NGN"
        tx_ref = str(uuid.uuid4())
        redirect_url = f"{BASE_URL}/payment-status/"

        Transaction.objects.create(
            ref=tx_ref,
            cart=cart,
            user=user,
            amount=total,
            currency=currency,
            status='pending'
        )

        payload = {
            "tx_ref": tx_ref,
            "amount": str(total),
            "currency": currency,
            "redirect_url": redirect_url,
            "customer": {
                "email": user.email,
                "name": user.username,
                "phonenumber": getattr(user, 'phone_number', '')
            },
            "customizations": {
                "title": "ShopNow Payment"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)

        if response.status_code in [200, 201]:
            return Response(response.json())
        return Response({"error": "Flutterwave API error", "details": response.json()}, status=response.status_code)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET", "POST"])
def payment_callback(request):
    transaction_id = request.GET.get("transaction_id")
    tx_ref = request.GET.get("tx_ref")
    status_param = request.GET.get("status")

    if not all([transaction_id, tx_ref, status_param]):
        return Response({
            "message": "Missing query parameters",
            "subMessage": "Transaction verification failed due to missing data."
        }, status=400)

    if status_param not in ["completed", "successful"]:
        return Response({
            "message": "Payment was not successful",
            "subMessage": "Try again or use another method."
        }, status=400)

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
    }

    try:
        verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        response = requests.get(verify_url, headers=headers)
        res_data = response.json()

        if res_data.get("status") == "success":
            # Mark transaction as complete
            transaction = Transaction.objects.filter(ref=tx_ref).first()
            if transaction:
                transaction.status = "completed"
                transaction.save()
                cart = transaction.cart
                cart.paid = True
                cart.save()
            return Response({'message': 'Payment verified successfully'})

        return Response({
            'message': 'Payment verification failed',
            'subMessage': 'Could not verify with Flutterwave.'
        }, status=400)

    except Exception as e:
        return Response({
            'message': 'Verification error',
            'subMessage': str(e)
        }, status=500)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_paypal_payment(request):
    try:
        user = request.user
        tx_ref = str(uuid.uuid4())
        cart_code = request.data.get("cart_code")
        if not cart_code:
            return Response({"error": "cart_code is required."}, status=400)

        cart = get_object_or_404(Cart, cart_code=cart_code)
        subtotal = sum(item.quantity * item.product.price for item in cart.items.all())
        tax = Decimal("1000.00")
        total_amount = subtotal + tax

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{BASE_URL}/paypal-payment-callback/?ref={tx_ref}",
                "cancel_url": f"{BASE_URL}/paypal-payment-callback/?ref={tx_ref}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Cart Items",
                        "sku": "cart",
                        "price": str(total_amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD"
                },
                "description": "ShopNow Payment"
            }]
        })

        if payment.create():
            Transaction.objects.create(
                ref=tx_ref,
                cart=cart,
                user=user,
                amount=total_amount,
                currency="USD",
                status='pending'
            )
            for link in payment.links:
                if link.rel == "approval_url":
                    return Response({"approval_url": str(link.href)})
            return Response({"error": "No approval URL found."}, status=400)
        else:
            return Response({"error": "PayPal payment creation failed.", "details": payment.error}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["POST"])
def paypal_payment_callback(request):
    payment_id = request.data.get("paymentId") or request.query_params.get("paymentId")
    payer_id = request.data.get("PayerID") or request.query_params.get("PayerID")
    ref = request.data.get("ref") or request.query_params.get("ref")

    transaction = get_object_or_404(Transaction, ref=ref)

    if payment_id and payer_id:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            transaction.status = "completed"
            transaction.save()
            cart = transaction.cart
            cart.paid = True
            if request.user.is_authenticated:
                cart.user = request.user
            cart.save()
            return Response({"message": "Payment successful"})
        return Response({"error": "Payment execution failed"}, status=400)

    return Response({"error": "Invalid callback parameters"}, status=400)