from django.contrib import admin
from django.utils.html import format_html
from .models import Products, Cart, CartItem, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("slug", "image_preview")
    list_display = ("name", "formatted_price", "category", "image_preview")
    fields = ("name", "slug", "image", "image_preview", "description", "price", "category")
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        fallback_url = "https://res.cloudinary.com/dorjc6aib/image/upload/v1730468123/default.jpg"
        image_url = None

        if getattr(obj, "image", None) and hasattr(obj.image, "url"):
            image_url = obj.image.url

        if not image_url:
            image_url = fallback_url

        return format_html(
            '<div style="text-align:center;">'
            '<img src="{}" width="100" style="object-fit:contain; border-radius:4px; border:1px solid #ddd;" />'
            '</div>',
            image_url,
        )
    image_preview.short_description = "Image Preview"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_code", "user", "paid", "created_at", "modified_at")
    list_filter = ("paid",)
    search_fields = ("cart_code", "user__username")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    search_fields = ("cart__cart_code", "product__name")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_preview")

    def image_preview(self, obj):
        fallback_url = "https://res.cloudinary.com/dorjc6aib/image/upload/v1730468123/default.jpg"
        image_url = None

        if getattr(obj, "image", None) and hasattr(obj.image, "url"):
            image_url = obj.image.url

        if not image_url:
            image_url = fallback_url

        return format_html(
            '<div style="text-align:center;">'
            '<img src="{}" width="100" style="object-fit:contain; border-radius:4px; border:1px solid #ddd;" />'
            '</div>',
            image_url,
        )
    image_preview.short_description = "Preview"
