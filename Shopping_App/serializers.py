from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Products, Cart, CartItem, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()


# ✅ Extra images for a product
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)  # ensures full Cloudinary URL

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


# ✅ Main Product Serializer
class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # show image URL properly
    extra_images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    category_display = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'slug', 'image', 'description', 'category',
            'category_display', 'formatted_price', 'extra_images', 'uploaded_images'
        ]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url  # ✅ Cloudinary gives full URL
            except:
                return None
        # Fallback default image
        return "https://res.cloudinary.com/dorjc6aib/image/upload/v123456/default.jpg"

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_formatted_price(self, obj):
        return obj.formatted_price  # property in model

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Products.objects.create(**validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)
        return instance


# ✅ Pagination
class ProductsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ✅ Detail view with similar products
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


# ✅ Cart item serializer with total calculation
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product", "total"]

    def get_total(self, obj):
        return obj.product.price * obj.quantity


# ✅ Full cart serializer with nested items
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


# ✅ Lightweight cart
class SimpleCartSerializer(serializers.ModelSerializer):
    num_of_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "num_of_items"]

    def get_num_of_items(self, cart):
        return sum(item.quantity for item in cart.items.all())


# ✅ Paid items for a user
class NewCartItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    order_id = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'order_id', 'order_date']

    def get_order_id(self, obj):
        return obj.cart.cart_code

    def get_order_date(self, obj):
        return obj.cart.modified_at


# ✅ Full User + purchase history
class UserSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'city', 'state', 'address', 'phone', 'items'
        ]

    def get_items(self, user):
        cart_items = CartItem.objects.filter(cart__user=user, cart__paid=True)[:10]
        return NewCartItemSerializer(cart_items, many=True).data


# ✅ Signup serializer
class CustomUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name', 'city', 'state', 'address', 'phone'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
