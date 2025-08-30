from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUsers

class CustomUsersAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'city', 'state', 'address', 'phone', 'is_active')
        }),
    )

admin.site.register(CustomUsers, CustomUsersAdmin)
