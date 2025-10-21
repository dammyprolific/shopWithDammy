from django.contrib import admin
from .models import Products, Cart, CartItem, ProductImage
from django.utils.html import format_html

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'image_preview',)
    list_display = ('name', 'price', 'formatted_price', 'category', 'image_preview')
    fields = ('name', 'slug', 'image', 'image_preview', 'description', 'price', 'category')
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = 'Image Preview'

admin.site.register(Products, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ProductImage)