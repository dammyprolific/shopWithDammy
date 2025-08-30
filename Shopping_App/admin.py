from django.contrib import admin
from .models import Products, Cart, CartItem, ProductImage
from django.utils.html import format_html
from django.contrib.admin.sites import AlreadyRegistered


class ProductImageInline(admin.TabularInline):  # or StackedInline
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'image_preview',)
    list_display = ('name', 'price', 'category', 'image_preview')
    fields = ('name', 'slug', 'image', 'image_preview', 'description', 'price', 'category')
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "(No image)"
    
    image_preview.short_description = 'Image Preview'

# ✅ Register models properly
try:
    admin.site.register(Products, ProductAdmin)
except AlreadyRegistered:
    pass
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ProductImage)
