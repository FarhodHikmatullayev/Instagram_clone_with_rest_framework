from django.contrib import admin
from .models import User, UserConfirmation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'auth_type', 'auth_status']


@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', "verify_type", "expiration_time"]

# gmail -> Pass@gmail.com
