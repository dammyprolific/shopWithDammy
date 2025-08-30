from rest_framework import serializers
from .models import Products, Cart, CartItem, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductsSerializer(serializers.ModelSerializer):
    extra_images = ProductImageSerializer(many=True, read_only=True)
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = ['id', 'name', 'slug', 'image', 'description', 'category', 'category_display', 'price', 'extra_images']

    def get_category_display(self, obj):
        # Uses Django's built-in method to get the human-readable choice
        return obj.get_category_display()


class DetailProductSerializer(serializers.ModelSerializer):
    similar_products = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = ['id', 'name', 'price', 'slug', 'image', 'description', 'category', 'category_display', 'similar_products']

    def get_similar_products(self, obj):
        similar = Products.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
        return ProductsSerializer(similar, many=True).data

    def get_category_display(self, obj):
        return obj.get_category_display()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product", "total"]

    def get_total(self, cart_item):
        return cart_item.product.price * cart_item.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(read_only=True, many=True)
    sum_total = serializers.SerializerMethodField()
    num_of_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "items", "sum_total", "num_of_items", "created_at", "modified_at"]

    def get_sum_total(self, cart):
        return sum(item.product.price * item.quantity for item in cart.items.all())

    def get_num_of_items(self, cart):
        return sum(item.quantity for item in cart.items.all())


class SimpleCartSerializer(serializers.ModelSerializer):
    num_of_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "num_of_items"]

    def get_num_of_items(self, cart):
        return sum(item.quantity for item in cart.items.all())


class NewCartItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    order_id = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'order_id', 'order_date']

    def get_order_id(self, cart_item):
        return cart_item.cart.cart_code

    def get_order_date(self, cart_item):
        return cart_item.cart.modified_at


class UserSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'city',
            'state',
            'address',
            'phone',
            'items'
        ]

    def get_items(self, user):
        cart_items = CartItem.objects.filter(cart__user=user, cart__paid=True)[:10]
        return NewCartItemSerializer(cart_items, many=True).data


class CustomUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'city', 'state', 'address', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
